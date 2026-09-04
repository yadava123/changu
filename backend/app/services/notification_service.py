from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Notification, NotificationPreference

from app.services.notification_templates import notification_template
from app.websocket.manager import manager
from sqlalchemy import event
from sqlalchemy.orm import Session as SqlAlchemySession


PREFERENCE_FIELDS = {
    "ORDER": "order_updates",
    "DELIVERY": "delivery_updates",
    "PAYMENT": "payment_updates",
    "PROMOTION": "promotions",
    "LOYALTY": "loyalty",
    "REFERRAL": "referrals",
    "SYSTEM": "system_notifications",
}

class NotificationService:
    @staticmethod
    def create_notification(db: Session, user_id: int, title: str, message: str, notification_type: str,
                            entity_type: str | None = None, entity_id: int | None = None,
                            event_key: str | None = None):
        preference_field = PREFERENCE_FIELDS.get(notification_type.split("_")[0])
        if preference_field:
            preference = db.scalar(select(NotificationPreference).where(NotificationPreference.user_id == user_id))
            if preference is not None and not getattr(preference, preference_field):
                return None
        scoped_key = f"{user_id}:{event_key}" if event_key else None
        if scoped_key and db.scalar(select(Notification).where(Notification.event_key == scoped_key)):
            return None
        item = Notification(user_id=user_id, title=title, message=message, type=notification_type,
                            entity_type=entity_type, entity_id=entity_id, event_key=scoped_key)
        db.add(item)
        db.flush()
        db.info.setdefault("notification_events", []).append((user_id, NotificationService.payload(item)))
        return item

    @staticmethod
    def from_template(db: Session, user_id: int, notification_type: str, template_name: str,
                      entity_type: str | None = None, entity_id: int | None = None,
                      event_key: str | None = None, **template_values):
        title, message = notification_template(template_name, **template_values)
        return NotificationService.create_notification(db, user_id, title, message, notification_type,
                                                       entity_type, entity_id, event_key)

    @staticmethod
    def payload(item: Notification) -> dict:
        return {"type": "NOTIFICATION", "entity_type": item.entity_type, "entity_id": item.entity_id,
                "data": {"id": item.id, "notification_type": item.type, "title": item.title,
                         "message": item.message, "is_read": item.is_read},
                "timestamp": (item.created_at or datetime.now(timezone.utc)).isoformat()}

    @staticmethod
    def send_order_notification(db,user_id,title,message,notification_type,order_id): return NotificationService.create_notification(db,user_id,title,message,notification_type,"ORDER",order_id,f"{order_id}:{notification_type}")
    @staticmethod
    def send_delivery_notification(db,user_id,title,message,notification_type,delivery_id): return NotificationService.create_notification(db,user_id,title,message,notification_type,"DELIVERY",delivery_id,f"{delivery_id}:{notification_type}")
    @staticmethod
    def send_siren_notification(db,user_id,title,message,notification_type,request_id): return NotificationService.create_notification(db,user_id,title,message,notification_type,"SIREN",request_id,f"{request_id}:{notification_type}")


@event.listens_for(SqlAlchemySession, "after_commit")
def publish_notifications(session):
    for user_id, message in session.info.pop("notification_events", []):
        manager.send_to_user_sync(user_id, message)
