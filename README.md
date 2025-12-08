MYST – Backend

Sistema de seguimiento clínico y ciclo menstrual
Versión inicial del entorno de desarrollo

Objetivo del proyecto

Proveer un backend que gestione información clínica, ciclos, recordatorios y contactos externos para el sistema Myst, utilizando FastAPI y PostgreSQL, con un entorno controlado, reproducible y documentado para garantizar orden y trazabilidad durante el desarrollo.

Integrantes

Rodrigo Pineda Salcedo
Valeria Estefania Salazar García
Jose Adrian Guillen Lamas
Ramses Alejandro López Anceno


Tecnologías utilizadas

Python 3.10+

FastAPI

SQLAlchemy

PostgreSQL

psycopg2

Uvicorn

Instrucciones para clonar

git clone https://github.com/Rodrichss/myst-backend.git

cd myst-backend

Configuración del entorno

Instalar dependencias:

pip install -r requirements.txt


Configura tu archivo .env:

DATABASE_URL=postgresql://myst_user:TU_PASSWORD@localhost:5432/myst_db

Ejecutar prueba de conexión

python test_db.py

Ejecutar el backend

uvicorn main:app --reload


El backend estará disponible en:

http://127.0.0.1:8000
