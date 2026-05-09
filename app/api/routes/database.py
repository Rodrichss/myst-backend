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

        # 3. Intentar convertir la columna 'type' a BOOLEAN si existe como VARCHAR
        try:
            # Usamos USING para decirle a Postgres cómo convertir el texto a booleano
            # Esto asume que 'true'/'1' -> True y 'false'/'0' -> False
            db.execute(text('''
                ALTER TABLE reminder
                ALTER COLUMN type TYPE BOOLEAN
                USING (type::boolean);
            '''))
            summary["reminder_type_fix"] = "Columna 'type' convertida de VARCHAR a BOOLEAN."
        except Exception as e:
            # Si la columna no existe aún, la creamos de una vez como BOOLEAN
            db.rollback()
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "type" BOOLEAN;'))
            summary["reminder_type_fix"] = "Columna 'type' creada como BOOLEAN."

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