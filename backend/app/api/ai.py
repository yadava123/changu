from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from app.ai.intent import Intent, detect_intent
from app.ai import tools
from app.ai.prompts import SYSTEM_PROMPT
from app.ai.provider import GroqProvider, GeminiProvider, RulesProvider
from app.api.dependencies import get_current_user, require_role
from app.db.session import get_db
from app.models import AIConversation, AIMessage, AIMessageRole, AIUsage, User, UserRole
from app.recommendation.service import RecommendationService
from app.core.config import settings
from app.core.rate_limit import enforce_rate_limit
from fastapi import Request

router=APIRouter(prefix="/api/ai",tags=["ai"])
class ChatRequest(BaseModel): message:str=Field(min_length=1,max_length=2000); conversation_id:int|None=None
class ConversationCreate(BaseModel): title:str="New Chat"

def own_conversation(cid,user,db):
    c=db.scalar(select(AIConversation).where(AIConversation.id==cid,AIConversation.user_id==user.id))
    if not c: raise HTTPException(404,"Conversation not found")
    return c

def result(item,kind):
    return {"type":kind,"id":item.id,"name":getattr(item,"name",getattr(item,"business_name","")),"price":str(getattr(item,"price","")) if hasattr(item,"price") else None,"action":f"VIEW_{kind.upper()}"}

@router.post("/conversations")
def create_conversation(payload:ConversationCreate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    c=AIConversation(user_id=user.id,title=payload.title); db.add(c); db.commit(); db.refresh(c); return c
@router.get("/conversations")
def conversations(user:User=Depends(get_current_user),db:Session=Depends(get_db)): return db.scalars(select(AIConversation).where(AIConversation.user_id==user.id).order_by(AIConversation.updated_at.desc())).all()
@router.get("/conversations/{conversation_id}")
def conversation(conversation_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    c=own_conversation(conversation_id,user,db); return {"id":c.id,"title":c.title,"messages":db.scalars(select(AIMessage).where(AIMessage.conversation_id==c.id).order_by(AIMessage.created_at)).all()}
@router.delete("/conversations/{conversation_id}",status_code=204)
def delete_conversation(conversation_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)): db.delete(own_conversation(conversation_id,user,db)); db.commit()

@router.post("/chat")
async def chat(payload:ChatRequest,request:Request,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if settings.rate_limit_enabled: enforce_rate_limit(request, f"ai:{user.id}", settings.ai_daily_request_limit, 86400)
    since=datetime.now(timezone.utc)-timedelta(days=1); used=db.scalar(select(func.coalesce(func.sum(AIUsage.request_count),0)).where(AIUsage.user_id==user.id,AIUsage.created_at>=since)) or 0
    if used >= settings.ai_daily_request_limit: raise HTTPException(429,"You've reached today's AI usage limit.")
    c=own_conversation(payload.conversation_id,user,db) if payload.conversation_id else AIConversation(user_id=user.id,title=payload.message[:80])
    if not payload.conversation_id: db.add(c); db.flush()
    db.add(AIMessage(conversation_id=c.id,role=AIMessageRole.USER,content=payload.message)); intent=detect_intent(payload.message); results=[]; actions=[]; text="I can help you search ChanGu, check your orders, explain your cart, or explain Siren."
    if intent==Intent.FOOD_SEARCH:
        query=payload.message.lower().replace('vegetarian','').replace('food','').strip() or 'food'; items=tools.search_food(db,query); results=[result(x,'food') for x in items]; text=f"I found {len(results)} food option(s) from the current ChanGu catalog." if results else "I couldn't find that food in the current ChanGu catalog."
    elif intent==Intent.PRODUCT_SEARCH:
        items=tools.search_products(db,payload.message); results=[result(x,'product') for x in items]; text=f"I found {len(results)} product(s) from the current ChanGu catalog." if results else "I couldn't find matching products."
    elif intent==Intent.RESTAURANT_SEARCH:
        items=tools.search_restaurants(db,payload.message); results=[result(x,'restaurant') for x in items]; text=f"I found {len(results)} restaurant(s)." if results else "I couldn't find matching restaurants."
    elif intent==Intent.ORDER_HISTORY:
        orders=tools.get_order_history(db,user); text="Here are your recent orders: " + (", ".join(f"{o.order_number} — {o.status.value}" for o in orders) if orders else "You have no orders yet.")
    elif intent==Intent.ORDER_STATUS:
        import re; match=re.search(r"CHG\d+",payload.message.upper()); order=tools.get_order_status(db,user,match.group(0)) if match else None; text=f"Your order {order.order_number} is currently {order.status.value.replace('_',' ').lower()}." if order else "I couldn't find that order in your account."
    elif intent==Intent.PARCEL_STATUS:
        import re; match=re.search(r"(?:parcel|package)\s*#?(\d+)",payload.message.lower()); parcel=tools.get_parcel_status(db,user,int(match.group(1)) if match else None); text=f"Parcel #{parcel.id} is currently {parcel.status.value.replace('_',' ').lower()}. Payment is {parcel.payment_status.value.lower()}." if parcel else "I couldn't find that parcel in your account."
    elif intent==Intent.RIDE_STATUS:
        import re; match=re.search(r"ride\s*#?(\d+)",payload.message.lower()); ride=tools.get_ride_status(db,user,int(match.group(1)) if match else None); text=f"Ride #{ride.id} is currently {ride.status.value.replace('_',' ').lower()}." if ride else "I couldn't find that ride in your account."
    elif intent==Intent.CART_INFORMATION:
        cart=tools.get_cart(db,user); text="Your cart is empty." if not cart.items else "You currently have: " + ", ".join(f"{i.name} x {i.quantity}" for i in cart.items) + f". Total ₹{cart.total}."
    elif intent==Intent.SIREN_INFORMATION:
        text=tools.get_siren_information()["message"]; actions=["OPEN_SIREN"]
    elif any(word in payload.message.lower() for word in ("what should i order", "recommend", "recommendation")):
        recs=RecommendationService.food(db,user.id,limit=6); results=recs; text="Based on your recent ChanGu activity, you might like these." if results else "I don't have enough activity yet, so keep exploring ChanGu to get personalized recommendations."
    context = "Verified ChanGu context: " + (", ".join(f"{item.get('name')} ({item.get('type')})" for item in results) if results else text)
    provider_name = "rules"
    if settings.ai_provider.lower() != "rules":
        messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":f"{payload.message}\n\n{context}"}]
        providers=[]
        if settings.ai_provider.lower() == "gemini": providers.append(("gemini",GeminiProvider()))
        if settings.ai_provider.lower() == "groq": providers.append(("groq",GroqProvider()))
        if settings.groq_api_key and settings.ai_provider.lower() != "groq": providers.append(("groq",GroqProvider()))
        if settings.gemini_api_key and settings.ai_provider.lower() != "gemini": providers.append(("gemini",GeminiProvider()))
        for name, provider in providers:
            try:
                text=await provider.generate(messages, {"fallback":text}); provider_name=name; break
            except Exception:
                continue
    db.add(AIMessage(conversation_id=c.id,role=AIMessageRole.ASSISTANT,content=text)); db.add(AIUsage(user_id=user.id,conversation_id=c.id,provider=provider_name,request_count=1,estimated_tokens=len(payload.message.split()))); db.commit()
    return {"conversation_id":c.id,"message":text,"intent":intent,"results":results,"actions":actions}

@router.get("/health")
def health(user:User=Depends(require_role(UserRole.ADMIN))):
    configured = settings.ai_provider.lower() == "rules" or bool(settings.gemini_api_key or settings.groq_api_key)
    return {"configured":configured,"provider":settings.ai_provider.lower(),"available":configured}

@router.get("/analytics")
def analytics(user:User=Depends(require_role(UserRole.ADMIN)),db:Session=Depends(get_db)):
    total=db.scalar(select(func.coalesce(func.sum(AIUsage.request_count),0))) or 0; intents=[]
    return {"total_requests":total,"successful_requests":total,"failed_requests":0,"average_latency_ms":0,"top_intents":intents}
