"""
Inicialización del paquete api.

Este archivo agrupa todos los routers de la carpeta api para que puedan
registrarse fácilmente en una aplicación FastAPI principal.
"""

from fastapi import APIRouter

from api.routes_health import router as health_router
from api.routes_zonas import router as zonas_router
from api.routes_mediciones import router as mediciones_router


# Router general de la API.
# Aquí metemos dentro todos los routers pequeños.
api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(zonas_router)
api_router.include_router(mediciones_router)