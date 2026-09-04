from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models import FoodItem, Product, Restaurant, UserEvent
from app.recommendation.rules import rank_food, rank_products

class RecommendationEngine:
    def recommend(self, user_id, context=None): raise NotImplementedError

class RuleBasedRecommendationEngine(RecommendationEngine):
    def recommend(self, user_id, context=None): return rank_food(context, user_id)

class RecommendationService:
    @staticmethod
    def food(db: Session, user_id: int, limit=10): return [{"type":"food","id":item.id,"name":item.name,"price":str(item.price),"category":item.category,"reason":reason,"score":score} for score,item,reason in rank_food(db,user_id,limit)]
    @staticmethod
    def products(db: Session, user_id: int, limit=10): return [{"type":"product","id":item.id,"name":item.name,"price":str(item.price),"category":item.category,"reason":reason,"score":score} for score,item,reason in rank_products(db,user_id,limit)]
    @staticmethod
    def restaurants(db: Session, user_id: int, limit=10): return [{"type":"restaurant","id":item.id,"name":item.name,"reason":"Popular near you","score":0} for item in db.scalars(select(Restaurant).where(Restaurant.is_active.is_(True)).limit(limit)).all()]
    @staticmethod
    def trending(db: Session, limit=10):
        rows=db.execute(select(UserEvent.entity_type,UserEvent.entity_id,func.count(UserEvent.id).label("count")).where(UserEvent.created_at >= func.datetime('now','-30 day'),UserEvent.entity_type.in_(["FOOD","PRODUCT"])).group_by(UserEvent.entity_type,UserEvent.entity_id).order_by(func.count(UserEvent.id).desc()).limit(limit)).all()
        return [{"type":row.entity_type.lower(),"id":row.entity_id,"score":row.count,"reason":"Trending now"} for row in rows]
    @staticmethod
    def recently_viewed(db: Session, user_id: int, limit=10):
        events=db.scalars(select(UserEvent).where(UserEvent.user_id==user_id,UserEvent.event_type.in_(["VIEW_FOOD","VIEW_PRODUCT","VIEW_RESTAURANT"])).order_by(UserEvent.created_at.desc()).limit(40)).all()
        seen=set(); result=[]
        for event in events:
            key=(event.entity_type,event.entity_id)
            if key not in seen: seen.add(key); result.append(event)
            if len(result)>=limit: break
        return [{"type":event.entity_type.lower(),"id":event.entity_id,"reason":"Recently viewed"} for event in result]
