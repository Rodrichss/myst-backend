from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from app.core.config import DATABASE_URL

load_dotenv()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def test_connection():
    try:
        with engine.connect() as conn:
            print("Conexión exitosa a PostgreSQL")
    except SQLAlchemyError as e:
        print("Error de conexión:", str(e))
