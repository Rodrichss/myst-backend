from fastapi import FastAPI
from app.db.database import engine
from app.db.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Myst API",
    description="Backend para la aplicación Myst",
    version="1.0"
)

@app.get("/")
def root():
    return {"message": "API funcionando"}
