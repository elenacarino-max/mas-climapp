"""
Rutas de comprobación de estado de la API.

Este archivo contiene endpoints sencillos para saber si la API
está funcionando correctamente.
"""

# APIRouter permite crear grupos de rutas separados del archivo principal.
from fastapi import APIRouter


# Creamos un router para las rutas de salud de la API.
# prefix="/health" significa que todas las rutas de este archivo
# empezarán por /health.
router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("/")
def health_check():
    """
    GET /health/

    Comprueba si la API está funcionando.
    Este endpoint es útil para pruebas rápidas.
    """
    return {
        "status": "ok",
        "mensaje": "API funcionando correctamente",
    }