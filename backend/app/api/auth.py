from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db
from app.models import DriverApplication, DriverApplicationStatus, EmergencyProvider, ProviderApplication, VendorApplication
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    RoleRegisterRequest,
    PublicUserResponse,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
    PasswordChangeRequest,
    ProfileUpdateRequest,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def find_user(db: Session, identifier: str) -> User | None:
    normalized = identifier.strip().lower()
    return db.scalar(select(User).where((User.email == normalized) | (User.phone == identifier.strip())))


def role_value(value: str) -> UserRole:
    try:
        return UserRole(value.upper())
    except ValueError:
        raise HTTPException(status_code=404, detail="Authentication route not found") from None


def role_mismatch(user: User, expected: UserRole) -> HTTPException:
    labels = {role: role.value.title().replace("_", " ") for role in UserRole}
    return HTTPException(status_code=403, detail=f"This account is registered as a {labels[user.role]}. Please use {labels[user.role]} Login.")


def check_role_status(user: User, expected: UserRole, db: Session) -> None:
    if user.role != expected:
        raise role_mismatch(user, expected)
    if expected == UserRole.VENDOR and not db.scalar(select(VendorApplication).where(VendorApplication.user_id == user.id, VendorApplication.status == "APPROVED")):
        raise HTTPException(status_code=403, detail="Your vendor account is waiting for admin approval.")
    if expected == UserRole.DRIVER:
        driver = db.scalar(select(DriverApplication).where(DriverApplication.user_id == user.id, DriverApplication.status == DriverApplicationStatus.APPROVED))
        if not driver:
            raise HTTPException(status_code=403, detail="Your driver account is waiting for admin approval.")
    if expected == UserRole.EMERGENCY_PROVIDER and not db.scalar(select(EmergencyProvider).where(EmergencyProvider.user_id == user.id, EmergencyProvider.is_active.is_(True), EmergencyProvider.is_verified.is_(True))):
        raise HTTPException(status_code=403, detail="Your emergency provider account is waiting for admin approval.")


def token_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user_id=user.id, email=user.email, role=user.role.value), token_type="bearer", user=PublicUserResponse.model_validate(user))


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)) -> RegisterResponse:
    if settings.rate_limit_enabled: enforce_rate_limit(request, f"register:{request.client.host if request.client else 'unknown'}", settings.register_rate_limit)
    email = str(payload.email).lower()
    if find_user_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
    if db.scalar(select(User).where(User.phone == payload.phone)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this phone already exists.")

    user = User(
        full_name=payload.full_name,
        email=email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email or phone already exists.") from None
    db.refresh(user)
    return RegisterResponse(message="Registration successful", user=PublicUserResponse.model_validate(user))


@router.post("/register/{role}", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_role(role: str, payload: RoleRegisterRequest, request: Request, db: Session = Depends(get_db)) -> RegisterResponse:
    if settings.rate_limit_enabled: enforce_rate_limit(request, f"register:{request.client.host if request.client else 'unknown'}", settings.register_rate_limit)
    expected = role_value(role)
    if expected == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin accounts can only be created by a super admin.")
    if find_user_by_email(db, str(payload.email)) or db.scalar(select(User).where(User.phone == payload.phone)):
        raise HTTPException(status_code=409, detail="An account with this email or phone already exists.")
    required = {UserRole.VENDOR: ("business_name", "business_type", "description", "address", "area", "city", "state", "pincode"), UserRole.DRIVER: ("vehicle_type", "vehicle_number", "license_number", "address", "area", "city", "state", "pincode"), UserRole.EMERGENCY_PROVIDER: ("provider_type", "business_name", "contact_name", "address", "area", "city", "state", "pincode")}
    missing = [field for field in required.get(expected, ()) if getattr(payload, field) in (None, "")]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required fields: {', '.join(missing)}")
    user = User(full_name=payload.full_name, email=str(payload.email).lower(), phone=payload.phone, password_hash=hash_password(payload.password), role=expected)
    db.add(user)
    db.flush()
    common = {"user_id": user.id, "phone": payload.phone, "email": str(payload.email).lower(), "address": payload.address, "area": payload.area, "city": payload.city, "state": payload.state, "pincode": payload.pincode}
    if expected == UserRole.VENDOR:
        db.add(VendorApplication(business_name=payload.business_name, business_type=payload.business_type, description=payload.description, **common))
    elif expected == UserRole.DRIVER:
        db.add(DriverApplication(full_name=payload.full_name, vehicle_type=payload.vehicle_type, vehicle_number=payload.vehicle_number, license_number=payload.license_number, **common))
    elif expected == UserRole.EMERGENCY_PROVIDER:
        db.add(ProviderApplication(provider_type=payload.provider_type, business_name=payload.business_name, contact_name=payload.contact_name, **common))
    db.commit()
    db.refresh(user)
    return RegisterResponse(message="Registration successful. Your account is pending approval." if expected != UserRole.CUSTOMER else "Registration successful", user=PublicUserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    return login_for_role(None, payload, request, db)


@router.post("/login/{role}", response_model=TokenResponse)
def login_for_role(role: str | None, payload: LoginRequest, request: Request, db: Session = Depends(get_db)) -> TokenResponse:
    if settings.rate_limit_enabled: enforce_rate_limit(request, f"login:{request.client.host if request.client else 'unknown'}", settings.login_rate_limit)
    user = find_user(db, payload.email)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    if role:
        check_role_status(user, role_value(role), db)
    return token_response(user)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
def update_profile(payload: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> UserResponse:
    current_user.full_name = payload.full_name
    current_user.phone = payload.phone
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
def change_password(payload: PasswordChangeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"status": "ok"}
