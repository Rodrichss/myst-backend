from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.reminder import Reminder
from app.models.user import User
from app.models.contact import Contact
from app.schemas.reminder import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    MedicationCreate
)

router = APIRouter(
    prefix="/reminders",
    tags=["Reminders"]
)

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

# Create medication reminder (private)
@router.post("/medication", response_model=ReminderResponse)
def create_medication_reminder(
    data: ReminderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminder = Reminder(
        id_user=current_user.id_user,
        title=data.title,
        start_date=data.start_date,
        end_date=data.end_date,
        day_time=data.day_time,
        after_meal=data.after_meal,
        dosage=data.dosage,
        type=True,  # medicamento
        status=0
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

# Get my medication reminders (private)
@router.get("/medication", response_model=list[ReminderResponse])
def get_my_medication_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminders = (
        db.query(Reminder)
        .filter(
            Reminder.id_user == current_user.id_user,
            Reminder.type == True
        )
        .order_by(Reminder.start_date, Reminder.day_time)
        .all()
    )
    return reminders

# Get reminders by contact (private)
@router.get("/contact/{id_contact}", response_model=list[ReminderResponse])
def get_reminders_by_contact(
    id_contact: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Verificar primero que el contacto pertenezca al usuario
    contact = (
        db.query(Contact)
        .filter(
            Contact.id_contact == id_contact,
            Contact.id_user == current_user.id_user
        )
        .first()
    )

    if not contact:
        raise HTTPException(404, "Contact not found or does not belong to user")

    # 2. Obtener los recordatorios asociados a ese contacto
    # Ordenados por fecha de inicio y hora (del más próximo al más lejano)
    reminders = (
        db.query(Reminder)
        .filter(Reminder.id_contact == id_contact)
        .order_by(Reminder.start_date.asc(), Reminder.day_time.asc())
        .all()
    )

    return reminders

# Get my reminders (private)
@router.get("/me", response_model=list[ReminderResponse])
def get_my_reminders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reminders = (
        db.query(Reminder)
        .filter(Reminder.id_user == current_user.id_user)
        .order_by(Reminder.start_date, Reminder.day_time)
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