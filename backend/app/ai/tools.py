from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.api.cart import cart_response, get_or_create_cart
from app.models import FoodItem, Order, Parcel, Product, Restaurant, Ride, User

def search_food(db:Session,query:str,city:str|None=None):
    term=f"%{query}%"; stmt=select(FoodItem).where(FoodItem.is_available.is_(True),or_(FoodItem.name.ilike(term),FoodItem.description.ilike(term),FoodItem.category.ilike(term)))
    return db.scalars(stmt.limit(10)).all()
def search_products(db:Session,query:str,category:str|None=None):
    term=f"%{query}%"; stmt=select(Product).where(Product.is_available.is_(True),or_(Product.name.ilike(term),Product.description.ilike(term),Product.category.ilike(term)))
    if category: stmt=stmt.where(Product.category.ilike(category))
    return db.scalars(stmt.limit(10)).all()
def search_restaurants(db:Session,query:str,city:str|None=None):
    term=f"%{query}%"; stmt=select(Restaurant).where(Restaurant.is_active.is_(True),or_(Restaurant.name.ilike(term),Restaurant.description.ilike(term)))
    if city: stmt=stmt.where(Restaurant.city.ilike(city))
    return db.scalars(stmt.limit(10)).all()
def get_order_status(db:Session,user:User,order_number:str): return db.scalar(select(Order).where(Order.user_id==user.id,Order.order_number==order_number))
def get_order_history(db:Session,user:User): return db.scalars(select(Order).where(Order.user_id==user.id).order_by(Order.created_at.desc()).limit(10)).all()
def get_parcel_status(db:Session,user:User,parcel_id:int|None=None):
    stmt=select(Parcel).where(Parcel.customer_id==user.id)
    if parcel_id: stmt=stmt.where(Parcel.id==parcel_id)
    return db.scalar(stmt.order_by(Parcel.created_at.desc()))
def get_ride_status(db:Session,user:User,ride_id:int|None=None):
    stmt=select(Ride).where(Ride.customer_id==user.id)
    if ride_id: stmt=stmt.where(Ride.id==ride_id)
    return db.scalar(stmt.order_by(Ride.created_at.desc()))
def get_cart(db:Session,user:User): return cart_response(get_or_create_cart(user,db))
def get_food_details(db:Session,food_id:int): return db.get(FoodItem,food_id)
def get_product_details(db:Session,product_id:int): return db.get(Product,product_id)
def get_siren_information(): return {"message":"ChanGu Siren connects customers with registered providers. For immediate life-threatening emergencies, contact official emergency services.","action":"OPEN_SIREN"}
