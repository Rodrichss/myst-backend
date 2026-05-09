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
        # 1. TABLA 'users'
        try:
            db.execute(text('ALTER TABLE users ALTER COLUMN picture TYPE VARCHAR(255);'))
            db.execute(text('ALTER TABLE users ADD COLUMN IF NOT EXISTS "last_verification_sent" TIMESTAMP;'))
            db.commit()
            summary["users_table"] = "Columna 'picture' ampliada y 'last_verification_sent' añadida."
        except Exception as e:
            db.rollback()
            summary["users_table"] = f"Error: {str(e)}"

        # 2. NUEVA TABLA 'address'
        try:
            db.execute(text('''
                CREATE TABLE IF NOT EXISTS address (
                    id_address SERIAL PRIMARY KEY,
                    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
                    name VARCHAR(100) NOT NULL,
                    street VARCHAR(200) NOT NULL,
                    neighborhood VARCHAR(100),
                    city VARCHAR(100) NOT NULL,
                    state VARCHAR(100) NOT NULL,
                    zip_code VARCHAR(10),
                    phone_number VARCHAR(20),
                    is_selected BOOLEAN NOT NULL DEFAULT FALSE
                );
            '''))
            # Crear índice para búsqueda rápida por usuario
            db.execute(text('CREATE INDEX IF NOT EXISTS ix_address_id_address ON address (id_address);'))
            db.commit()
            summary["address_table"] = "Tabla 'address' creada exitosamente."
        except Exception as e:
            db.rollback()
            summary["address_table"] = f"Error: {str(e)}"

        # 3. TABLA 'contact' - Actualización y Relación con Address
        try:
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "about" VARCHAR(250);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "specialty" VARCHAR(50);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "genre" INTEGER;'))
            
            # Añadir FK a address si no existe
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "id_address" INTEGER REFERENCES address(id_address) ON DELETE SET NULL;'))

            # Eliminar restricciones UNIQUE
            db.execute(text('ALTER TABLE contact DROP CONSTRAINT IF EXISTS contact_email_key;'))
            db.execute(text('ALTER TABLE contact DROP CONSTRAINT IF EXISTS contact_phone_number_key;'))
            db.execute(text('DROP INDEX IF EXISTS ix_contact_email;'))
            db.execute(text('DROP INDEX IF EXISTS ix_contact_phone_number;'))

            db.commit()
            summary["contact_table"] = "Campos actualizados, restricciones eliminadas y relación con 'address' añadida."
        except Exception as e:
            db.rollback()
            summary["contact_table"] = f"Error en contact: {str(e)}"

        # 4. TABLA 'reminder' - BOOLEAN fix
        try:
            db.execute(text('''
                ALTER TABLE reminder 
                ALTER COLUMN type TYPE BOOLEAN 
                USING (type::boolean);
            '''))
            db.commit()
            summary["reminder_type_fix"] = "Columna 'type' convertida a BOOLEAN."
        except Exception as e:
            db.rollback()
            db.execute(text('ALTER TABLE reminder ADD COLUMN IF NOT EXISTS "type" BOOLEAN;'))
            db.commit()
            summary["reminder_type_fix"] = "Columna 'type' verificada/creada como BOOLEAN."

        # 5. OTROS (clinical_history, cycle)
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