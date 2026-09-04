from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base
from app.models import AIConversation, AIMessage, AIUsage, Address, AuditLog, Cart, CartItem, Coupon, CouponUsage, Delivery, Driver, DriverApplication, EmergencyProvider, EmergencyRequest, Favorite, FoodItem, LoyaltyAccount, LoyaltyTransaction, Notification, NotificationPreference, Order, OrderItem, Parcel, PaymentTransaction, PlatformSetting, Product, ProviderApplication, RecommendationEvent, RecommendationFeedback, Referral, Restaurant, Review, Ride, User, UserEvent, UserPreference, Vendor, VendorApplication

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url or "sqlite:///./changu.db")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata, literal_binds=True, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
