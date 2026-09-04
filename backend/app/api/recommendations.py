from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import Favorite, User, UserEvent, UserPreference, RecommendationEvent, RecommendationFeedback
from app.recommendation.service import RecommendationService

router=APIRouter(prefix="/api",tags=["recommendations"])
class EventRequest(BaseModel): event_type:str; entity_type:str|None=None; entity_id:int|None=None; metadata:dict|None=None
class PreferenceUpdate(BaseModel): preferred_categories:list[str]=[]; preferred_food_types:list[str]=[]; preferred_product_categories:list[str]=[]; preferred_restaurants:list[int]=[]; preferred_price_range:str|None=None; personalization_enabled:bool=True; memory_enabled:bool=True; recommendations_enabled:bool=True
class FavoriteRequest(BaseModel): entity_type:str; entity_id:int
class FeedbackRequest(BaseModel): entity_type:str; entity_id:int; feedback:str
@router.post('/events',status_code=201)
def event(payload:EventRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    preference=db.scalar(select(UserPreference).where(UserPreference.user_id==user.id))
    if preference and not preference.memory_enabled: return {"status":"disabled"}
    values=payload.model_dump(); metadata=values.pop("metadata"); db.add(UserEvent(user_id=user.id,metadata_json=metadata,**values)); db.commit(); return {"status":"recorded"}
@router.get('/preferences')
def preferences(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    p=db.scalar(select(UserPreference).where(UserPreference.user_id==user.id)); return p or {"personalization_enabled":True,"memory_enabled":True,"recommendations_enabled":True,"preferred_categories":[]}
@router.patch('/preferences')
def update_preferences(payload:PreferenceUpdate,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    p=db.scalar(select(UserPreference).where(UserPreference.user_id==user.id))
    if not p:p=UserPreference(user_id=user.id);db.add(p)
    for key,value in payload.model_dump().items():setattr(p,key,value)
    db.commit();db.refresh(p);return p
@router.delete('/preferences',status_code=204)
def clear_preferences(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    p=db.scalar(select(UserPreference).where(UserPreference.user_id==user.id))
    if p: db.delete(p)
    db.query(UserEvent).filter(UserEvent.user_id==user.id).delete(synchronize_session=False)
    db.commit()
@router.get('/favorites')
def favorites(user:User=Depends(get_current_user),db:Session=Depends(get_db)):return db.scalars(select(Favorite).where(Favorite.user_id==user.id)).all()
@router.post('/favorites')
def favorite(payload:FavoriteRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=Favorite(user_id=user.id,**payload.model_dump());db.add(item);db.add(UserEvent(user_id=user.id,event_type='FAVORITE',entity_type=payload.entity_type,entity_id=payload.entity_id));db.commit();return item
@router.delete('/favorites/{favorite_id}')
def unfavorite(favorite_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=db.scalar(select(Favorite).where(Favorite.id==favorite_id,Favorite.user_id==user.id))
    if not item:raise HTTPException(404,'Favorite not found')
    db.delete(item);db.commit();return {'status':'removed'}
@router.get('/recommendations/home')
def home(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    p=db.scalar(select(UserPreference).where(UserPreference.user_id==user.id)); enabled=not p or (p.personalization_enabled and p.recommendations_enabled); personalized=RecommendationService.food(db,user.id) if enabled else []
    if not enabled: return {"personalized":[],"recently_viewed":[],"popular_nearby":[],"trending":[],"continue_shopping":[]}
    return {"personalized":personalized,"recently_viewed":RecommendationService.recently_viewed(db,user.id),"popular_nearby":RecommendationService.restaurants(db,user.id),"trending":RecommendationService.trending(db),"continue_shopping":personalized[:4]}
@router.get('/recommendations/food')
def food(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    p=db.scalar(select(UserPreference).where(UserPreference.user_id==user.id)); return {"type":"PERSONALIZED","items":RecommendationService.food(db,user.id) if not p or (p.personalization_enabled and p.recommendations_enabled) else []}
@router.get('/recommendations/products')
def products(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    p=db.scalar(select(UserPreference).where(UserPreference.user_id==user.id)); return {"type":"PERSONALIZED","items":RecommendationService.products(db,user.id) if not p or (p.personalization_enabled and p.recommendations_enabled) else []}
@router.get('/recommendations/restaurants')
def restaurants(user:User=Depends(get_current_user),db:Session=Depends(get_db)):return {"type":"PERSONALIZED","items":RecommendationService.restaurants(db,user.id)}
@router.get('/recommendations/trending')
def trending(user:User=Depends(get_current_user),db:Session=Depends(get_db)):return {"type":"TRENDING","items":RecommendationService.trending(db)}
@router.get('/recommendations/recently-viewed')
def recent(user:User=Depends(get_current_user),db:Session=Depends(get_db)):return {"type":"RECENTLY_VIEWED","items":RecommendationService.recently_viewed(db,user.id)}
@router.get('/recommendations/similar/{entity_type}/{entity_id}')
def similar(entity_type:str,entity_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):return {"type":"SIMILAR_ITEMS","items":[]}
@router.post('/recommendations/feedback')
def feedback(payload:FeedbackRequest,user:User=Depends(get_current_user),db:Session=Depends(get_db)):db.add(RecommendationFeedback(user_id=user.id,**payload.model_dump()));db.commit();return {'status':'recorded'}
@router.get('/admin/recommendations/analytics')
def analytics(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    if user.role.value!='ADMIN':raise HTTPException(403,'Access denied')
    shown=db.query(RecommendationEvent).count(); clicked=db.query(RecommendationEvent).filter(RecommendationEvent.event_type=='recommendation_clicked').count(); purchased=db.query(RecommendationEvent).filter(RecommendationEvent.event_type=='recommendation_purchased').count()
    return {'shown':shown,'clicked':clicked,'click_through_rate':clicked/shown if shown else 0,'purchased':purchased,'conversion_rate':purchased/clicked if clicked else 0}
