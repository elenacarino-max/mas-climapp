import os
from sqlalchemy import create_engine           # crea la conexión con la base de datos
from sqlalchemy.orm import sessionmaker        # fábrica de sesiones (una sesión = una conversación con la BD)
from sqlalchemy.orm import declarative_base    # clase base de la que heredan todos los modelos
from dotenv import load_dotenv                 # lee el archivo .env y mete las variables en os.environ

# Lee el archivo .env si existe. Debe llamarse antes de cualquier os.getenv()
# para que las variables del .env estén disponibles.
load_dotenv()

# Intenta leer DATABASE_URL del .env.
# Si no existe esa variable (por ejemplo en local sin .env), usa SQLite con el
# mismo archivo clima.db del Proyecto 2, así no rompemos nada del P2.
# Formato SQLite:  "sqlite:///./clima.db"      (ruta relativa al directorio actual)
# Formato Postgres: "postgresql://user:pass@host/dbname"  (si en el futuro se migra)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./clima.db")

# El engine es el objeto que sabe cómo hablar con la base de datos.
# Solo hay uno en toda la aplicación (es caro de crear).
# connect_args={"check_same_thread": False} es obligatorio en SQLite cuando se usa
# con FastAPI porque FastAPI puede llamar a la BD desde distintos hilos.
# En PostgreSQL u otras BD esto no hace falta, por eso lo condicionamos.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# SessionLocal es una clase (no una sesión todavía).
# Cada vez que hagamos SessionLocal() crearemos UNA sesión nueva.
# autocommit=False → los cambios no se guardan solos, hay que llamar a db.commit() explícitamente.
# autoflush=False  → SQLAlchemy no manda los cambios a la BD antes de cada consulta automáticamente.
# bind=engine      → le decimos a qué base de datos se conectan las sesiones que cree esta fábrica.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base es la clase madre de todos los modelos (Zona, Medicion...).
# Cuando un modelo hereda de Base, SQLAlchemy sabe que esa clase representa una tabla.
# También guarda un registro de todas las tablas para poder crearlas con create_all().
Base = declarative_base()


def get_db():
    """
    Generador de sesión para inyectar como dependencia en los endpoints de FastAPI.

    Por qué es un generador (usa yield en vez de return):
        FastAPI necesita que la sesión esté abierta DURANTE toda la petición
        y que se cierre AL FINAL, tanto si todo fue bien como si hubo un error.
        Con yield conseguimos ese comportamiento: el código después del yield
        se ejecuta cuando FastAPI termina de usar la sesión.

    Cómo lo usa la Persona 4 en un endpoint:
        from fastapi import Depends
        from sqlalchemy.orm import Session
        from db.database import get_db

        @app.get("/mediciones")
        def listar(db: Session = Depends(get_db)):
            # db es una sesión abierta y lista para usar
            return db.query(Medicion).all()
        # al salir de la función, FastAPI llama al finally y cierra la sesión
    """
    db = SessionLocal()   # abre una sesión nueva para esta petición
    try:
        yield db          # cede la sesión al endpoint; aquí se pausa el generador
    finally:
        db.close()        # esto siempre se ejecuta, haya error o no


def create_tables():
    """
    Crea todas las tablas en la base de datos si no existen todavía.
    Es necesario importar models aquí para que SQLAlchemy los registre
    en Base.metadata antes de llamar a create_all().
    """
    from db import models  # noqa: F401 — import necesario para registrar los modelos
    Base.metadata.create_all(bind=engine)