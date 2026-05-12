"""
Archivo principal de la API REST de Mas ClimApp.

Este archivo es el punto de entrada de FastAPI.
Aquí se crea la aplicación principal y se conectan las rutas
separadas en la carpeta api/.

Para arrancar la API desde terminal:

    uvicorn main_api:app --reload

Después se puede abrir la documentación automática en:

    http://127.0.0.1:8000/docs
"""

# Importamos FastAPI, que es la herramienta principal para crear la API.
from fastapi import FastAPI

# Importamos los routers de la carpeta api.
# Cada router contiene un grupo de endpoints relacionados.
from api.routes_health import router as health_router
from api.routes_mediciones import router as mediciones_router
from api.routes_zonas import router as zonas_router


# Creamos la aplicación principal de FastAPI.
# Estos datos aparecerán en la documentación automática de Swagger.
app = FastAPI(
    title="Mas ClimApp API",
    description="API REST para gestionar zonas y mediciones climáticas.",
    version="1.0.0",
)


# Conectamos el router de health check.
# Sirve para comprobar rápidamente si la API está funcionando.
app.include_router(health_router)


# Conectamos el router de mediciones.
# Aquí estarán los endpoints relacionados con mediciones climáticas.
app.include_router(mediciones_router)


# Conectamos el router de zonas.
# Aquí estarán los endpoints relacionados con zonas.
app.include_router(zonas_router)


@app.get("/")
def root():
    """
    Endpoint raíz de la API.

    Sirve como comprobación inicial para saber que la API está viva.
    """
    return {
        "mensaje": "Mas ClimApp API funcionando correctamente",
        "docs": "Visita /docs para probar los endpoints",
    }