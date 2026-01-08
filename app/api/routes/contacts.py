from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.contact import Contact
from app.models.user import User
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ContactResponse)
def create_contact(
    data: ContactCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == data.id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    contact = Contact(**data.dict())
    db.add(contact)
    db.commit()
    db.refresh(contact)

    return contact

@router.get(
    "/user/{id_user}",
    response_model=list[ContactResponse]
)
def get_contacts_by_user(
    id_user: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Contact)
        .filter(Contact.id_user == id_user)
        .all()
    )

@router.patch(
    "/{id_contact}",
    response_model=ContactResponse
)
def update_contact(
    id_contact: int,
    data: ContactUpdate,
    db: Session = Depends(get_db)
):
    contact = (
        db.query(Contact)
        .filter(Contact.id_contact == id_contact)
        .first()
    )

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)

    return contact

@router.delete("/{id_contact}")
def delete_contact(
    id_contact: int,
    db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter(Contact.id_contact == id_contact).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"detail": "Contact deleted"}