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
    try:
        # 1. Cambios en la tabla 'cycle'
        # Añadimos position si no existe, y eliminamos 'order'
        db.execute(text('ALTER TABLE cycle ADD COLUMN IF NOT EXISTS "position" INTEGER;'))
        
        # OJO: Según tu migración '859670558dcd', luego decides borrar position. 
        # Si realmente ya NO la quieres, descomenta la siguiente línea:
        # db.execute(text('ALTER TABLE cycle DROP COLUMN IF EXISTS "position";'))
        
        db.execute(text('ALTER TABLE cycle DROP COLUMN IF EXISTS "order";'))

        # 2. Cambios en 'clinical_history'
        db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "last_period_date" DATE;'))
        db.execute(text('ALTER TABLE clinical_history ADD COLUMN IF NOT EXISTS "regularity" VARCHAR(10);'))

        # 3. Foreign Key en 'daily_logs' (Solo si no existe)
        # PostgreSQL no tiene "ADD CONSTRAINT IF NOT EXISTS" de forma directa y sencilla, 
        # pero podemos intentar añadirla capturando si ya existe o asumiendo que es necesaria.
        try:
            db.execute(text('''
                ALTER TABLE daily_logs 
                ADD CONSTRAINT fk_daily_logs_cycle 
                FOREIGN KEY (id_cycle) REFERENCES cycle (id_cycle);
            '''))
        except Exception:
            # Si falla es porque probablemente la constraint ya existe
            db.rollback() 
        
        db.commit()
        return {"status": "success", "message": "Database schema updated to match latest migrations"}
    
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}