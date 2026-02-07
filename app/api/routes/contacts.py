from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.core.dependencies import get_current_user, get_db

from app.models.user import User
from app.models.contact import Contact
from app.schemas.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse
)

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)

# Create contact (private)
@router.post("/", response_model=ContactResponse)
def create_contact(
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = Contact(
        **data.dict(),
        id_user=current_user.id_user
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact

# List my contacts (private)
@router.get("/", response_model=list[ContactResponse])
def list_my_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Contact)
        .filter(Contact.id_user == current_user.id_user)
        .all()
    )


# Update my contact (private)
@router.patch("/{id_contact}", response_model=ContactResponse)
def update_contact(
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
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact


# Delete my contact (private)
@router.delete("/{id_contact}")
def delete_contact(
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
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"detail": "Contact deleted"}