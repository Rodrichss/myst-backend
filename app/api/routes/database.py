from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.dependencies import get_db

router = APIRouter(
    prefix="/database",
    tags=["Database"]
)
@router.get("/fix-database")
def fix_db(db: Session = Depends(get_db)):
    try:
        # 1. Cambios en la tabla 'cycle'
        db.execute(text('ALTER TABLE cycle ADD COLUMN IF NOT EXISTS "position" INTEGER;'))
        db.execute(text('ALTER TABLE cycle DROP COLUMN IF EXISTS "order";'))

        # 2. Cambios en 'clinical_history'
        db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "last_period_date" DATE;'))
        db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "regularity" VARCHAR(10);'))

        # 3. NUEVOS CAMBIOS: Tabla 'contact'
        # Añadimos los nuevos campos solicitados
        db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "about" VARCHAR(250);'))
        db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "specialty" VARCHAR(50);'))
        db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "genre" INTEGER;'))

        # 4. Foreign Key en 'daily_logs'
        try:
            db.execute(text('''
                ALTER TABLE daily_logs
                ADD CONSTRAINT fk_daily_logs_cycle
                FOREIGN KEY (id_cycle) REFERENCES cycle (id_cycle);
            '''))
        except Exception:
            # Si falla, es porque la constraint ya existe
            db.rollback()

        db.commit()
        return {"status": "success", "message": "Database schema updated with contact fields and migrations"}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}