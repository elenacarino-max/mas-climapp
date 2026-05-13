"""
Archivo principal de FastAPI para la API REST del Proyecto 3.

IMPORTANTE:
Este archivo NO sustituye al app.py de Flask.
Tu app.py sigue siendo la aplicación web con Flask.

Este archivo sirve para levantar la API REST con FastAPI usando Uvicorn.
"""

from fastapi import FastAPI

from api import api_router
from db.database import create_tables


# Creamos la aplicación FastAPI.
# Esta variable se llama "app" porque Uvicorn buscará:
#     api.main:app
app = FastAPI(
    title="MAS ClimApp API",
    description="API REST para gestionar zonas y mediciones climáticas",
    version="1.0.0"
)


@app.on_event("startup")
def iniciar_api():
    """
    Esta función se ejecuta automáticamente al arrancar FastAPI.

    create_tables():
        Crea las tablas en la base de datos si todavía no existen.

    Esto usa los modelos de db/models.py:
        - Zona
        - Medicion
    """
    create_tables()


@app.get("/")
def inicio():
    """
    Ruta raíz de la API.

    Sirve para comprobar rápidamente que FastAPI está funcionando.
    """
    return {
        "message": "MAS ClimApp API funcionando",
        "docs": "/docs",
        "health": "/health/",
        "zonas": "/zonas/",
        "mediciones": "/mediciones/"
    }


# Conectamos todos los routers definidos en api/__init__.py:
# - routes_health.py
# - routes_zonas.py
# - routes_mediciones.py
app.include_router(api_router)