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
        # --- NUEVO: CORRECCIÓN DE TAMAÑO PARA URL DE FIREBASE ---
        try:
            # Cambiamos el tipo de dato de picture a 255 para que quepan los links de Firebase
            db.execute(text('ALTER TABLE users ALTER COLUMN picture TYPE VARCHAR(255);'))
            db.commit()
            summary["users_table"] = "Columna 'picture' ampliada a 255 caracteres."
        except Exception as e:
            db.rollback()
            summary["users_table"] = f"Error al ampliar picture: {str(e)}"

        # 1. TABLA 'contact' - (Tu código anterior...)
        try:
            db.execute(text('ALTER TABLE contact ADD COLUMN IF NOT EXISTS "about" VARCHAR(250);'))
            # ... resto de tu código de contact ...
            db.commit()
            summary["contact_table"] = "Columnas 'about', 'specialty', 'genre' verificadas."
        except Exception as e:
            db.rollback()
            summary["contact_table"] = f"Error en contact: {str(e)}"

        # ... (Resto de los pasos 2, 3 y 4 que ya tienes) ...

        return {
            "status": "success",
            "message": "Migración manual finalizada, incluyendo ampliación de columna picture",
            "details": summary
        }

    except Exception as e:
        db.rollback()
        return {"status": "error", "error_detail": str(e)}