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
        # 1. TABLA 'contact' - Los campos que faltaban
        # Hacemos commit individual para asegurar que estas columnas se guarden
        try:
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "about" VARCHAR(250);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "specialty" VARCHAR(50);'))
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "genre" INTEGER;'))
            db.commit()
            summary["contact_table"] = "Columnas 'about', 'specialty', 'genre' verificadas/añadidas."
        except Exception as e:
            db.rollback()
            summary["contact_table"] = f"Error en contact: {str(e)}"

        # 2. TABLA 'cycle'
        try:
            db.execute(text('ALTER TABLE cycle ADD COLUMN IF NOT EXISTS "position" INTEGER;'))
            db.execute(text('ALTER TABLE cycle DROP COLUMN IF EXISTS "order";'))
            db.commit()
            summary["cycle_table"] = "Columna 'position' añadida y 'order' eliminada."
        except Exception as e:
            db.rollback()
            summary["cycle_table"] = f"Error en cycle: {str(e)}"

        # 3. TABLA 'clinical_history'
        try:
            db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "last_period_date" DATE;'))
            db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "regularity" VARCHAR(10);'))
            db.commit()
            summary["clinical_history"] = "Nuevos campos de historia clínica añadidos."
        except Exception as e:
            db.rollback()
            summary["clinical_history"] = f"Error en clinical_history: {str(e)}"

        # 4. CONSTRAINT en 'daily_logs'
        # Esto suele fallar si ya existe, por eso tiene su propio try/except/rollback
        try:
            db.execute(text('''
                ALTER TABLE daily_logs
                ADD CONSTRAINT fk_daily_logs_cycle
                FOREIGN KEY (id_cycle) REFERENCES cycle (id_cycle);
            '''))
            db.commit()
            summary["constraints"] = "Foreign Key fk_daily_logs_cycle creada con éxito."
        except Exception:
            db.rollback()
            summary["constraints"] = "La constraint ya existía o el ID no coincide (Saltado)."

        # --- VERIFICACIÓN FINAL ---
        # Consultamos a la base de datos qué columnas existen realmente ahora mismo
        check_cols = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='contact'
            AND column_name IN ('about', 'specialty', 'genre');
        """)).fetchall()

        columns_in_db = [row[0] for row in check_cols]
        summary["db_verification_current_columns"] = columns_in_db

        return {
            "status": "success",
            "message": "Proceso de migración manual finalizado",
            "details": summary
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": "Error crítico en el script",
            "error_detail": str(e)
        }