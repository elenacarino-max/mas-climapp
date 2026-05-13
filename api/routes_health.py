"""
Rutas de salud de la API.

Este archivo sirve para comprobar rápidamente que la API está viva
y que la conexión con la base de datos funciona correctamente.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from db.database import get_db


# Creamos un router específico para health.
# prefix="/health" significa que todas estas rutas empezarán por /health.
router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("/")
def comprobar_api():
    """
    Endpoint básico para comprobar que la API responde.

    URL final:
        GET /health/

    Devuelve un mensaje sencillo si el servidor está funcionando.
    """
    return {
        "status": "ok",
        "message": "API funcionando correctamente"
    }


@router.get("/db")
def comprobar_base_datos(db: Session = Depends(get_db)):
    """
    Endpoint para comprobar que la conexión con la base de datos funciona.

    URL final:
        GET /health/db

    Depends(get_db):
        FastAPI abre una sesión de base de datos,
        la usa dentro de esta función y la cierra al terminar.
    """
    try:
        # Consulta mínima para verificar que la BD responde.
        db.execute(text("SELECT 1"))

        return {
            "status": "ok",
            "database": "conectada"
        }

    except Exception as error:
        # Si algo falla en la conexión, devolvemos un error 500.
        raise HTTPException(
            status_code=500,
            detail=f"Error de conexión con la base de datos: {error}"
        )