from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.address import Address
from app.models.user import User
from app.schemas.commerce import AddressRequest, AddressResponse

router = APIRouter(prefix="/api/addresses", tags=["addresses"])


def own_address(address_id: int, user: User, db: Session) -> Address:
    address = db.scalar(select(Address).where(Address.id == address_id, Address.user_id == user.id))
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


def save_default(address: Address, db: Session):
    if address.is_default:
        db.execute(update(Address).where(Address.user_id == address.user_id, Address.id != address.id).values(is_default=False))


@router.get("", response_model=list[AddressResponse])
def list_addresses(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Address).where(Address.user_id == user.id).order_by(Address.is_default.desc(), Address.created_at.desc())).all()


@router.post("", response_model=AddressResponse, status_code=201)
def create_address(payload: AddressRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    address = Address(user_id=user.id, **payload.model_dump())
    db.add(address)
    db.flush()
    save_default(address, db)
    db.commit()
    db.refresh(address)
    return address


@router.patch("/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, payload: AddressRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    address = own_address(address_id, user, db)
    for key, value in payload.model_dump().items():
        setattr(address, key, value)
    save_default(address, db)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}", status_code=204)
def delete_address(address_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    address = own_address(address_id, user, db)
    db.delete(address)
    db.commit()
