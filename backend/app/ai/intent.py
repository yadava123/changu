from enum import StrEnum

class Intent(StrEnum):
    FOOD_SEARCH="FOOD_SEARCH"; PRODUCT_SEARCH="PRODUCT_SEARCH"; RESTAURANT_SEARCH="RESTAURANT_SEARCH"; ORDER_STATUS="ORDER_STATUS"; ORDER_HISTORY="ORDER_HISTORY"; PARCEL_STATUS="PARCEL_STATUS"; RIDE_STATUS="RIDE_STATUS"; PRODUCT_DETAILS="PRODUCT_DETAILS"; FOOD_DETAILS="FOOD_DETAILS"; CART_INFORMATION="CART_INFORMATION"; VENDOR_INFORMATION="VENDOR_INFORMATION"; SIREN_INFORMATION="SIREN_INFORMATION"; GENERAL_HELP="GENERAL_HELP"; UNKNOWN="UNKNOWN"

def detect_intent(message: str) -> Intent:
    text=message.lower()
    if any(word in text for word in ("cart", "basket")): return Intent.CART_INFORMATION
    if any(word in text for word in ("where is my order", "order status", "track order", "out for delivery")): return Intent.ORDER_STATUS
    if any(word in text for word in ("my orders", "recent orders", "order history")): return Intent.ORDER_HISTORY
    if any(word in text for word in ("parcel", "package")) and any(word in text for word in ("status", "track", "where", "in transit")): return Intent.PARCEL_STATUS
    if any(word in text for word in ("ride", "driver")) and any(word in text for word in ("status", "track", "where", "location", "latest")): return Intent.RIDE_STATUS
    if any(word in text for word in ("siren", "emergency", "towing", "breakdown", "fuel emergency")): return Intent.SIREN_INFORMATION
    if any(word in text for word in ("restaurant", "restaurants", "kitchen", "home chef")): return Intent.RESTAURANT_SEARCH
    if any(word in text for word in ("product", "products", "shop", "store", "grocery")): return Intent.PRODUCT_SEARCH
    if any(word in text for word in ("food", "biryani", "dosa", "meal", "vegetarian", "vegan")): return Intent.FOOD_SEARCH
    if any(word in text for word in ("how does", "help", "what can you")): return Intent.GENERAL_HELP
    return Intent.UNKNOWN
