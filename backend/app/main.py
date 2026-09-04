"""ChanGu API application entry point."""

import logging
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.db.session import engine
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.addresses import router as addresses_router
from app.api.cart import router as cart_router
from app.api.food import router as food_router
from app.api.orders import router as orders_router
from app.api.vendor import router as vendor_router
from app.api.admin import router as admin_router
from app.api.admin_drivers import router as admin_drivers_router
from app.api.driver import router as driver_router
from app.api.products import router as products_router
from app.api.routes import router
from app.api.restaurants import router as restaurants_router
from app.api.search import router as search_router
from app.api.siren import admin_router as siren_admin_router
from app.api.siren import customer_router as siren_customer_router
from app.api.siren import provider_router as siren_provider_router
from app.api.notifications import router as notifications_router
from app.api.ai import router as ai_router
from app.api.recommendations import router as recommendations_router
from app.api.admin_control import router as admin_control_router
from app.api.notification_preferences import router as notification_preferences_router
from app.api.payments import router as payments_router
from app.api.reviews import router as reviews_router
from app.api.earnings import router as earnings_router
from app.api.growth import router as growth_router
from app.api.transport import driver_transport_router, parcel_router, ride_router
from app.websocket.routes import router as websocket_router
from app.api.tracking import router as tracking_router, driver_router as driver_tracking_router, provider_router as provider_tracking_router
from app.core.config import settings

app = FastAPI(
    title="ChanGu API",
    description="Foundation API for India's hyperlocal commerce and assistance platform.",
    version="1.0.0",
)

logger = logging.getLogger("changu.api")


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request failed request_id=%s method=%s path=%s", request_id, request.method, request.url.path)
        response = JSONResponse(status_code=500, content={"detail": "Something went wrong. Please try again.", "request_id": request_id})
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' https: ws: wss:; img-src 'self' data:; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; frame-ancestors 'none'"
    logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%.2f", request_id, request.method, request.url.path, response.status_code, (time.perf_counter() - started) * 1000)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router)
app.include_router(addresses_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(vendor_router)
app.include_router(admin_router)
app.include_router(admin_drivers_router)
app.include_router(driver_router)
app.include_router(restaurants_router)
app.include_router(food_router)
app.include_router(products_router)
app.include_router(search_router)
app.include_router(siren_customer_router)
app.include_router(siren_provider_router)
app.include_router(siren_admin_router)
app.include_router(notifications_router)
app.include_router(ai_router)
app.include_router(recommendations_router)
app.include_router(admin_control_router)
app.include_router(notification_preferences_router)
app.include_router(payments_router)
app.include_router(reviews_router)
app.include_router(earnings_router)
app.include_router(growth_router)
app.include_router(parcel_router)
app.include_router(ride_router)
app.include_router(driver_transport_router)
app.include_router(websocket_router)
app.include_router(tracking_router)
app.include_router(driver_tracking_router)
app.include_router(provider_tracking_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, __):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/health/live", tags=["system"])
def live():
    return {"status": "ok"}


@app.get("/health/db", tags=["system"])
def health_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "degraded", "database": "unavailable"})


@app.get("/ready", tags=["system"])
def ready():
    result = health_db()
    if isinstance(result, JSONResponse):
        return JSONResponse(status_code=503, content={"ready": False})
    return {"ready": True}
