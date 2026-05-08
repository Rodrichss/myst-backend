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
        # 1. TABLA 'users' - Ampliar picture y añadir last_verification_sent
        try:
            db.execute(text('ALTER TABLE users ALTER COLUMN picture TYPE VARCHAR(255);'))
            db.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS "last_verification_sent" TIMESTAMP;'))
            db.commit()
            summary["users_table"] = "Columna 'picture' ampliada y 'last_verification_sent' añadida."
        except Exception as e:
            db.rollback()
            summary["users_table"] = f"Error: {str(e)}"

        # 2. TABLA 'contact' - Campos de perfil y eliminación de UNIQUE
        try:
            # Añadir columnas si no existen (lo que ya tenías)
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "about" VARCHAR(250);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "specialty" VARCHAR(50);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "genre" INTEGER;'))

            # ELIMINAR RESTRICCIONES UNIQUE (Email y Phone)
            # Usamos DROP CONSTRAINT IF EXISTS.
            # Los nombres estándar de SQLAlchemy/Postgres suelen ser estos:
            db.execute(text('ALTER TABLE contact DROP CONSTRAINT IF EXISTS contact_email_key;'))
            db.execute(text('ALTER TABLE contact DROP CONSTRAINT IF EXISTS contact_phone_number_key;'))

            # En algunos casos, si se crearon como índices simples:
            db.execute(text('DROP INDEX IF EXISTS ix_contact_email;'))
            db.execute(text('DROP INDEX IF EXISTS ix_contact_phone_number;'))

            db.commit()
            summary["contact_table"] = "Columnas actualizadas y restricciones UNIQUE eliminadas."
        except Exception as e:
            db.rollback()
            summary["contact_table"] = f"Error en contact: {str(e)}"

        # 3. TABLA 'reminder' - ACTUALIZACIÓN DE HORARIOS
        try:
            # A. Añadir nueva columna day_time
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "day_time" TIME;'))

            # B. Eliminar columnas obsoletas (si existen)
            db.execute(text('ALTER TABLE reminder DROP COLUMN IF EXISTS "start_time";'))
            db.execute(text('ALTER TABLE reminder DROP COLUMN IF EXISTS "end_time";'))

            # C. Asegurar integridad de campos obligatorios (start_date y status)
            # Primero permitimos nulos para añadir si no existen, luego llenamos y bloqueamos
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "start_date" DATE;'))
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "status" INTEGER;'))
            
            # Rellenar datos vacíos para evitar error de NOT NULL
            db.execute(text("UPDATE reminder SET start_date = CURRENT_DATE WHERE start_date IS NULL;"))
            db.execute(text("UPDATE reminder SET status = 0 WHERE status IS NULL;"))

            # Aplicar restricciones NOT NULL
            db.execute(text('ALTER TABLE reminder ALTER COLUMN start_date SET NOT NULL;'))
            db.execute(text('ALTER TABLE reminder ALTER COLUMN status SET NOT NULL;'))

            # D. Otros campos opcionales
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "end_date" DATE;'))
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "type" BOOLEAN;'))
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "dosage" VARCHAR(100);'))
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "after_meal" BOOLEAN;'))

            db.commit()
            summary["reminder_table"] = "Columnas start/end_time eliminadas. day_time añadida y esquema actualizado."
        except Exception as e:
            db.rollback()
            summary["reminder_table"] = f"Error en reminder: {str(e)}"

        # 4. Otros cambios (clinical_history, cycle, etc.)
        try:
            db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "last_period_date" DATE;'))
            db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "regularity" VARCHAR(10);'))
            db.execute(text('ALTER TABLE cycle ADD COLUMN IF NOT EXISTS "position" INTEGER;'))
            db.execute(text('ALTER TABLE cycle DROP COLUMN IF EXISTS "order";'))
            db.commit()
            summary["others"] = "Tablas 'clinical_history' y 'cycle' actualizadas."
        except Exception as e:
            db.rollback()
            summary["others"] = f"Error: {str(e)}"

        return {
            "status": "success",
            "message": "Sincronización de base de datos completada",
            "details": summary
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "error_detail": str(e)}