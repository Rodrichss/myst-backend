from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.dependencies import get_current_user, get_db

from app.models.user import User
from app.models.contact import Contact
from app.models.address import Address
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse
)

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)

def _validate_address(db: Session, id_address: int, id_user: int) -> None:
    """Verifica que la dirección exista y pertenezca al usuario."""
    address = db.query(Address).filter(
        Address.id_address == id_address,
        Address.id_user == id_user
    ).first()
    if not address:
        raise HTTPException(
            status_code=404,
            detail="Address not found or does not belong to this user"
        )


# Create contact (private)
@router.post("/", response_model=ContactResponse)
def create_contact(
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if data.id_address is not None:
        _validate_address(db, data.id_address, current_user.id_user)

    contact = Contact(
        **data.dict(),
        id_user=current_user.id_user
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact

# Get my contacts (private)
@router.get("/me", response_model=list[ContactResponse])
def get_my_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contacts = (
        db.query(Contact)
        .filter(Contact.id_user == current_user.id_user)
        .all()
    )

    return contacts

# Get one of my contacts (private)
@router.get("/me/{id_contact}", response_model=ContactResponse)
def get_my_contact(
    id_contact: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id_contact == id_contact,
            Contact.id_user == current_user.id_user
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact

# Update my contact (private)
@router.patch("/me/{id_contact}", response_model=ContactResponse)
def update_my_contact(
    id_contact: int,
    data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id_contact == id_contact,
            Contact.id_user == current_user.id_user
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )
    
    if data.id_address is not None:
        _validate_address(db, data.id_address, current_user.id_user)


    for key, value in data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)

    return contact


# Delete my contact (private)
@router.delete("/me/{id_contact}")
def delete_my_contact(
    id_contact: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = (
        db.query(Contact)
        .filter(
            Contact.id_contact == id_contact,
            Contact.id_user == current_user.id_user
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    db.delete(contact)
    db.commit()

    return {"detail": "Contact deleted"}