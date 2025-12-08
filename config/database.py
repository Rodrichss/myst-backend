from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql://myst_user:2345@localhost:5432/myst_db"

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
