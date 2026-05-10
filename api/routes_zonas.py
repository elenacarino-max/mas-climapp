"""
Rutas de zonas.

Este archivo contiene los endpoints relacionados con las zonas:
consultar, crear, actualizar y borrar zonas.

IMPORTANTE:
De momento usamos una lista en memoria como datos simulados.
Más adelante se sustituirá por llamadas al CRUD y a la base de datos.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel


# Creamos el router de zonas.
# Todas las rutas de este archivo empezarán por /zonas.
router = APIRouter(
    prefix="/zonas",
    tags=["Zonas"],
)


# ==========================================================
# SCHEMAS TEMPORALES
# ==========================================================
# Estos modelos sirven para validar los datos que llegan a la API.
# Son temporales hasta que el equipo cierre los schemas definitivos.


class ZonaCreate(BaseModel):
    """
    Datos necesarios para crear una zona.

    No incluimos id porque el sistema lo genera automáticamente.
    """

    nombre: str
    descripcion: str | None = None


class ZonaUpdate(BaseModel):
    """
    Datos necesarios para actualizar una zona.

    De momento pedimos todos los campos.
    Más adelante se puede adaptar si se quiere permitir PATCH parcial.
    """

    nombre: str
    descripcion: str | None = None


# ==========================================================
# DATOS SIMULADOS
# ==========================================================
# Esta lista actúa como una base de datos temporal.
# Cuando el CRUD esté terminado, esto se cambiará por funciones reales.

zonas = [
    {
        "id": 1,
        "nombre": "Norte",
        "descripcion": "Zona norte de la Comunidad de Madrid",
    },
    {
        "id": 2,
        "nombre": "Sur",
        "descripcion": "Zona sur de la Comunidad de Madrid",
    },
    {
        "id": 3,
        "nombre": "Centro",
        "descripcion": "Zona centro de la Comunidad de Madrid",
    },
]


# ==========================================================
# FUNCIONES AUXILIARES
# ==========================================================

def buscar_zona_por_id(zona_id: int):
    """
    Busca una zona dentro de la lista simulada.

    Si encuentra la zona, la devuelve.
    Si no la encuentra, devuelve None.
    """
    for zona in zonas:
        if zona["id"] == zona_id:
            return zona

    return None


# ==========================================================
# ENDPOINTS
# ==========================================================

@router.get("/")
def listar_zonas():
    """
    GET /zonas/

    Devuelve todas las zonas disponibles.
    """
    return zonas


@router.get("/{zona_id}")
def obtener_zona(zona_id: int):
    """
    GET /zonas/{zona_id}

    Devuelve una zona concreta según su ID.
    Si no existe, devuelve un error 404.
    """
    zona = buscar_zona_por_id(zona_id)

    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada",
        )

    return zona


@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_zona(nueva_zona: ZonaCreate):
    """
    POST /zonas/

    Crea una nueva zona.

    Recibe los datos en formato JSON.
    Devuelve código 201 porque se ha creado un recurso nuevo.
    """
    nuevo_id = max(zona["id"] for zona in zonas) + 1

    zona_creada = {
        "id": nuevo_id,
        "nombre": nueva_zona.nombre,
        "descripcion": nueva_zona.descripcion,
    }

    zonas.append(zona_creada)

    return zona_creada


@router.put("/{zona_id}")
def actualizar_zona(zona_id: int, datos_actualizados: ZonaUpdate):
    """
    PUT /zonas/{zona_id}

    Actualiza una zona completa.

    Si la zona no existe, devuelve 404.
    """
    zona = buscar_zona_por_id(zona_id)

    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada",
        )

    zona["nombre"] = datos_actualizados.nombre
    zona["descripcion"] = datos_actualizados.descripcion

    return zona


@router.delete("/{zona_id}")
def eliminar_zona(zona_id: int):
    """
    DELETE /zonas/{zona_id}

    Elimina una zona por ID.

    Si no existe, devuelve 404.
    """
    zona = buscar_zona_por_id(zona_id)

    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada",
        )

    zonas.remove(zona)

    return {
        "mensaje": f"Zona con ID {zona_id} eliminada correctamente"
    }