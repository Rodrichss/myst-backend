from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.dependencies import get_db

router = APIRouter(
    prefix="/database",
    tags=["Database"]
)
@router.get("/fix-database")
def fix_db(db:Session=Depends(get_db)):
    db.execute(text('ALTER TABLE cycle ADD COLUMN IF NOT EXISTS "position" INTEGER;'))
    db.commit()
    return {"message": "column added"}