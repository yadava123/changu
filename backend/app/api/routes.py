from fastapi import APIRouter

router = APIRouter()


@router.get("/", tags=["system"])
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to ChanGu API",
        "status": "running",
        "version": "1.0.0",
    }


@router.get("/api/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "changu-backend"}
