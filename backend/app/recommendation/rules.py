from sqlalchemy import select
from app.models import FoodItem, Product, Restaurant, UserEvent, UserPreference
from app.recommendation.scoring import event_score

def category_signals(events, preferences):
    categories = set((preferences.preferred_categories or []) + (preferences.preferred_food_types or []) + (preferences.preferred_product_categories or [])) if preferences else set()
    scores = {}
    for event in events:
        scores[event.entity_id] = scores.get(event.entity_id, 0) + event_score(event)
    return scores, categories

def rank_food(db, user_id, limit=10):
    events=db.scalars(select(UserEvent).where(UserEvent.user_id==user_id, UserEvent.entity_type=="FOOD").order_by(UserEvent.created_at.desc()).limit(100)).all()
    preference=db.scalar(select(UserPreference).where(UserPreference.user_id==user_id))
    scores,categories=category_signals(events,preference)
    items=db.scalars(select(FoodItem).where(FoodItem.is_available.is_(True)).limit(100)).all()
    ranked=[]
    for item in items:
        score=scores.get(item.id,0)+(8 if item.category in categories else 0)
        ranked.append((score,item,"Because you viewed similar food" if score else "Popular near you"))
    return sorted(ranked,key=lambda value:value[0],reverse=True)[:limit]

def rank_products(db, user_id, limit=10):
    events=db.scalars(select(UserEvent).where(UserEvent.user_id==user_id, UserEvent.entity_type=="PRODUCT").order_by(UserEvent.created_at.desc()).limit(100)).all()
    preference=db.scalar(select(UserPreference).where(UserPreference.user_id==user_id))
    scores,categories=category_signals(events,preference)
    items=db.scalars(select(Product).where(Product.is_available.is_(True)).limit(100)).all()
    ranked=[]
    for item in items:
        score=scores.get(item.id,0)+(8 if item.category in categories else 0)
        ranked.append((score,item,"Because you viewed similar products" if score else "Popular near you"))
    return sorted(ranked,key=lambda value:value[0],reverse=True)[:limit]
