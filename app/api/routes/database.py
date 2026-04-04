from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db

router = APIRouter()
@router.get("/fix-database")
def fix_db(db:Session=Depends(get_db)):
    db.execute('ALTER TABLE cycle ADD COLUMN "position" INTEGER;')
    db.commit()
    return {"message": "column added"}