from datetime import datetime, timezone
from math import exp

EVENT_WEIGHTS = {"PURCHASE": 10, "ADD_TO_CART": 8, "FAVORITE": 7, "VIEW_FOOD": 3, "VIEW_PRODUCT": 3, "VIEW_RESTAURANT": 3, "SEARCH": 2, "ORDER_COMPLETED": 10}

def recency_multiplier(created_at: datetime) -> float:
    age_days = max((datetime.now(timezone.utc) - created_at.replace(tzinfo=timezone.utc)).total_seconds() / 86400, 0)
    return exp(-age_days / 30)

def event_score(event) -> float:
    return EVENT_WEIGHTS.get(event.event_type, 0) * recency_multiplier(event.created_at)
