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
    summary = {}
    try:
        # 1. TABLA 'users': Ampliar picture y añadir last_verification_sent
        try:
            db.execute(text('ALTER TABLE users ALTER COLUMN picture TYPE VARCHAR(255);'))
            db.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS "last_verification_sent" TIMESTAMP;'))
            db.commit()
            summary["users_table"] = "Columna 'picture' ampliada y 'last_verification_sent' añadida."
        except Exception as e:
            db.rollback()
            summary["users_table"] = f"Error: {str(e)}"

        # 2. TABLA 'contact': Tus nuevos campos
        try:
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "about" VARCHAR(250);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "specialty" VARCHAR(50);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "genre" INTEGER;'))
            db.commit()
            summary["contact_table"] = "Campos 'about', 'specialty' y 'genre' añadidos."
        except Exception as e:
            db.rollback()
            summary["contact_table"] = f"Error: {str(e)}"

        # 3. TABLA 'reminder': Los cambios conflictivos de tu amigo
        # Usamos la técnica de 3 pasos: añadir como NULL -> llenar -> cambiar a NOT NULL
        try:
            # start_date
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "start_date" DATE;'))
            db.execute(text("UPDATE reminder SET start_date = '2026-04-28' WHERE start_date IS NULL;"))
            db.execute(text('ALTER TABLE reminder ALTER COLUMN start_date SET NOT NULL;'))
            
            # status
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "status" INTEGER;'))
            db.execute(text("UPDATE reminder SET status = 1 WHERE status IS NULL;"))
            db.execute(text('ALTER TABLE reminder ALTER COLUMN status SET NOT NULL;'))
            
            db.commit()
            summary["reminder_table"] = "Campos 'start_date' y 'status' actualizados con éxito."
        except Exception as e:
            db.rollback()
            summary["reminder_table"] = f"Error: {str(e)}"

        # 4. TABLA 'clinical_history' y 'cycle' (Limpieza de versiones anteriores)
        try:
            db.execute(text('ALTER TABLE cycle ADD COLUMN IF NOT EXISTS "position" INTEGER;'))
            db.execute(text('ALTER TABLE cycle DROP COLUMN IF EXISTS "order";'))
            db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "last_period_date" DATE;'))
            db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "regularity" VARCHAR(10);'))
            db.commit()
            summary["legacy_fixes"] = "Tablas 'cycle' y 'clinical_history' sincronizadas."
        except Exception as e:
            db.rollback()
            summary["legacy_fixes"] = f"Error: {str(e)}"

        return {
            "status": "success",
            "message": "Esquema de base de datos sincronizado con la rama principal",
            "details": summary
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "error_detail": str(e)}