from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
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

# Create reminder (private)
@router.post("/", response_model=ReminderResponse)
def create_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # validar contacto solo si viene
    if data.id_contact is not None:
        contact = (
            db.query(Contact)
            .filter(
                Contact.id_contact == data.id_contact,
                Contact.id_user == current_user.id_user
            )
            .first()
        )

        if not contact:
            raise HTTPException(400, "Invalid contact")

    reminder = Reminder(
        **data.dict(exclude={"id_user"}),
        id_user=current_user.id_user
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder

# Get my reminders (private)
@router.get("/me", response_model=list[ReminderResponse])
def get_my_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminders = (
        db.query(Reminder)
        .filter(Reminder.id_user == current_user.id_user)
        .order_by(Reminder.date, Reminder.time)
        .all()
    )

    return reminders

# Get one of my reminders (private)
@router.get("/me/{id_reminder}", response_model=ReminderResponse)
def get_my_reminder(
    id_reminder: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id_reminder == id_reminder,
            Reminder.id_user == current_user.id_user
        )
        .first()
    )

    if not reminder:
        raise HTTPException(404, "Reminder not found")

    return reminder

# Update my reminder (private)
@router.patch("/me/{id_reminder}", response_model=ReminderResponse)
def update_my_reminder(
    id_reminder: int,
    data: ReminderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id_reminder == id_reminder,
            Reminder.id_user == current_user.id_user
        )
        .first()
    )

    if not reminder:
        raise HTTPException(404, "Reminder not found")

    # validar contacto si se intenta cambiar
    if data.id_contact is not None:
        contact = (
            db.query(Contact)
            .filter(
                Contact.id_contact == data.id_contact,
                Contact.id_user == current_user.id_user
            )
            .first()
        )

        if not contact:
            raise HTTPException(400, "Invalid contact")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(reminder, key, value)

    db.commit()
    db.refresh(reminder)

    return reminder

# Delete my reminder (private)
@router.delete("/me/{id_reminder}")
def delete_my_reminder(
    id_reminder: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminder = (
        db.query(Reminder)
        .filter(
            Reminder.id_reminder == id_reminder,
            Reminder.id_user == current_user.id_user
        )
        .first()
    )

    if not reminder:
        raise HTTPException(404, "Reminder not found")

    db.delete(reminder)
    db.commit()

    return {"detail": "Reminder deleted"}