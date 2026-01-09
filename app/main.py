from fastapi import FastAPI

from app.db.database import engine
from app.db.base import Base

# Import routes
from app.api.routes import (
    users,
    clinical_history,
    cycles,
    contacts,
    reminders
)

# Create tables in the database (only for development)
# Base.metadata.create_all(bind=engine)
# GRANT ALL ON SCHEMA public TO myst_user; (sql)

app = FastAPI(
    title="Myst API",
    description="Backend de Myst - Salud menstrual y bienestar",
    version="1.0.0"
)

# Include routers
app.include_router(users.router)
app.include_router(clinical_history.router)
app.include_router(cycles.router)
app.include_router(contacts.router)
app.include_router(reminders.router)

@app.get("/")
def root():
    return {"message": "Myst API is running"}