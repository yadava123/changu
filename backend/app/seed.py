from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import FoodItem, Product, Restaurant, User, UserRole


def seed_admin() -> None:
    if not settings.admin_email or not settings.admin_password:
        raise RuntimeError("ADMIN_EMAIL and ADMIN_PASSWORD must be configured")
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.email == settings.admin_email.lower()))
        if existing:
            print("Admin account already exists; no changes made.")
            return
        admin = User(
            full_name="ChanGu Admin",
            email=settings.admin_email.lower(),
            phone="0000000000",
            password_hash=hash_password(settings.admin_password),
            role=UserRole.ADMIN,
        )
        db.add(admin)
        db.commit()
        print("Development admin account created.")


def seed_catalog() -> None:
    with SessionLocal() as db:
        owner = db.scalar(select(User).where(User.email == "development-owner@example.com"))
        if owner is None:
            owner = User(
                full_name="Development Catalog Owner",
                email="development-owner@example.com",
                phone="0000000001",
                password_hash=hash_password("DevelopmentOnlyPassword123"),
                role=UserRole.CUSTOMER,
            )
            db.add(owner)
            db.flush()

        if db.scalar(select(Restaurant).where(Restaurant.name == "Riya's Kitchen")):
            print("Development catalog already exists; no changes made.")
            return

        restaurants = [
            Restaurant(name="Riya's Kitchen", description="Homestyle Indian meals made fresh in Bengaluru.", owner_id=owner.id, phone="08000000001", address="Indiranagar, Bengaluru", city="Bengaluru"),
            Restaurant(name="Bengaluru Home Meals", description="Comforting regional recipes for everyday lunch.", owner_id=owner.id, phone="08000000002", address="Koramangala, Bengaluru", city="Bengaluru"),
            Restaurant(name="Local Spice Kitchen", description="Bold flavours, family recipes, and weekend specials.", owner_id=owner.id, phone="08000000003", address="Jayanagar, Bengaluru", city="Bengaluru"),
        ]
        db.add_all(restaurants)
        db.flush()
        db.add_all([
            FoodItem(restaurant_id=restaurants[0].id, name="Chicken Biryani", description="Fragrant basmati rice with tender chicken and house spices.", price=220, category="Indian"),
            FoodItem(restaurant_id=restaurants[0].id, name="Veg Meals", description="A wholesome plate of seasonal vegetables, dal, rice, and chapati.", price=160, category="Indian"),
            FoodItem(restaurant_id=restaurants[1].id, name="Chapati Curry", description="Soft chapatis served with a rotating homestyle curry.", price=140, category="Home Chef"),
            FoodItem(restaurant_id=restaurants[1].id, name="Idli Vada", description="Steamed idlis and crisp vada with chutney and sambar.", price=110, category="Breakfast"),
            FoodItem(restaurant_id=restaurants[2].id, name="Paneer Rice", description="Aromatic rice tossed with paneer, vegetables, and spices.", price=190, category="Indian"),
        ])
        db.add_all([
            Product(name="Organic Eggs", description="Farm fresh eggs from a local producer.", price=120, category="Grocery", seller_id=owner.id, stock_quantity=20),
            Product(name="Fresh Vegetables", description="A seasonal basket sourced from nearby growers.", price=280, category="Organic", seller_id=owner.id, stock_quantity=12),
            Product(name="Handmade Basket", description="A durable woven basket made by local artisans.", price=450, category="Handmade", seller_id=owner.id, stock_quantity=7),
            Product(name="Homemade Pickle", description="Small-batch mango pickle with a balanced spice blend.", price=180, category="Local Products", seller_id=owner.id, stock_quantity=15),
            Product(name="Local Honey", description="Raw honey collected from regional apiaries.", price=320, category="Organic", seller_id=owner.id, stock_quantity=10),
        ])
        db.commit()
        print("Development catalog data created.")


if __name__ == "__main__":
    if settings.admin_email and settings.admin_password:
        seed_admin()
    seed_catalog()
