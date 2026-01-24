from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.reminder import Reminder
from app.models.user import User
from app.models.contact import Contact
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse
)

router = APIRouter(
    prefix="/reminders",
    tags=["Reminders"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ReminderResponse)
def create_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id_user == data.id_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.id_contact is not None:
        contact = (
            db.query(Contact)
            .filter(Contact.id_contact == data.id_contact)
            .first()
        )
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")

    payload = data.dict()
    
    if payload["id_contact"] == 0:
        payload["id_contact"] = None

    reminder = Reminder(**payload)
    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder

@router.get(
    "/user/{id_user}",
    response_model=list[ReminderResponse]
)
def get_reminders_by_user(
    id_user: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(Reminder)
        .filter(Reminder.id_user == id_user)
        .order_by(Reminder.date, Reminder.time)
        .all()
    )

@router.patch(
    "/{id_reminder}",
    response_model=ReminderResponse
)
def update_reminder(
    id_reminder: int,
    data: ReminderUpdate,
    db: Session = Depends(get_db)
):
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id_reminder == id_reminder)
        .first()
    )

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(reminder, key, value)

    db.commit()
    db.refresh(reminder)

    return reminder

@router.delete("/{id_reminder}")
def delete_reminder(
    id_reminder: int,
    db: Session = Depends(get_db)
):
    reminder = db.query(Reminder).filter(Reminder.id_reminder == id_reminder).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    db.delete(reminder)
    db.commit()
    return {"detail": "Reminder deleted"}