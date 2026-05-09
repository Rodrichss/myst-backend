# app/api/routes/addresses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.address import Address
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse

router = APIRouter(
    prefix="/addresses",
    tags=["Addresses"]
)


# Create address (private)
@router.post("/", response_model=AddressResponse)
def create_address(
    data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Si la nueva dirección es is_selected, desmarcar las demás
    if data.is_selected:
        db.query(Address).filter(
            Address.id_user == current_user.id_user,
            Address.is_selected == True
        ).update({"is_selected": False})
        db.commit()

    address = Address(
        **data.dict(),
        id_user=current_user.id_user
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


# Get my addresses (private)
@router.get("/me", response_model=list[AddressResponse])
def get_my_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Address)
        .filter(Address.id_user == current_user.id_user)
        .order_by(Address.is_selected.desc(), Address.id_address.asc())
        .all()
    )


# Get one address (private)
@router.get("/me/{id_address}", response_model=AddressResponse)
def get_my_address(
    id_address: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id_address == id_address,
        Address.id_user == current_user.id_user
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address

# Select address as active (private)
@router.post("/me/{id_address}/select", response_model=AddressResponse)
def select_address(
    id_address: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id_address == id_address,
        Address.id_user == current_user.id_user
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
 
    # Desmarcar todas las demás
    db.query(Address).filter(
        Address.id_user == current_user.id_user,
        Address.id_address != id_address
    ).update({"is_selected": False})
 
    address.is_selected = True
    db.commit()
    db.refresh(address)
    return address


# Update address (private)
@router.patch("/me/{id_address}", response_model=AddressResponse)
def update_my_address(
    id_address: int,
    data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id_address == id_address,
        Address.id_user == current_user.id_user
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Si se está marcando como seleccionada, desmarcar las demás
    if data.is_selected:
        db.query(Address).filter(
            Address.id_user == current_user.id_user,
            Address.id_address != id_address,
            Address.is_selected == True
        ).update({"is_selected": False})
        db.commit()

    for key, value in data.dict(exclude_unset=True).items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)
    return address


# Delete address (private)
@router.delete("/me/{id_address}")
def delete_my_address(
    id_address: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    address = db.query(Address).filter(
        Address.id_address == id_address,
        Address.id_user == current_user.id_user
    ).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)
    db.commit()
    return {"detail": "Address deleted"}