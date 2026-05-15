"""
Rutas API para gestionar zonas.

Una zona representa un municipio o localización asociada a una estación meteorológica.

Este archivo conecta los endpoints de FastAPI con las funciones del archivo db/crud.py.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud


# Router específico para zonas.
# Todas las rutas de este archivo empezarán por /zonas.
router = APIRouter(
    prefix="/zonas",
    tags=["Zonas"]
)


# =========================================================
# SCHEMAS PYDANTIC
# =========================================================
# Los schemas sirven para validar los datos que entran y
# controlar los datos que salen en la respuesta de la API.


class ZonaBase(BaseModel):
    """
    Campos comunes de una zona.

    Estos nombres coinciden con los campos del modelo Zona en db/models.py:
        municipio
        cod_ine
        id_estacion
        estacion_referencia
    """

    municipio: str
    cod_ine: str
    id_estacion: str
    estacion_referencia: str


class ZonaCrear(ZonaBase):
    """
    Schema para crear una zona.

    Hereda todos los campos de ZonaBase.
    Al crear una zona, todos estos campos son obligatorios.
    """

    pass


class ZonaActualizar(BaseModel):
    """
    Schema para actualizar una zona.

    Todos los campos son opcionales porque en una actualización
    podemos cambiar solo municipio, solo cod_ine, solo estación, etc.
    """

    municipio: Optional[str] = None
    cod_ine: Optional[str] = None
    id_estacion: Optional[str] = None
    estacion_referencia: Optional[str] = None


class ZonaResponse(ZonaBase):
    """
    Schema de respuesta.

    Incluye el id, porque ese id lo genera la base de datos.
    """

    id: int

    # Permite que Pydantic convierta objetos SQLAlchemy en JSON.
    model_config = ConfigDict(from_attributes=True)


# =========================================================
# ENDPOINTS DE ZONAS
# =========================================================


@router.get("/", response_model=list[ZonaResponse])
def listar_zonas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Lista zonas existentes.

    URL:
        GET /zonas/

    Parámetros opcionales:
        skip  → cuántos registros saltar
        limit → cuántos registros devolver como máximo
    """

    return crud.obtener_zonas(db=db, skip=skip, limit=limit)


@router.get("/cod-ine/{cod_ine}", response_model=ZonaResponse)
def obtener_zona_por_cod_ine(
    cod_ine: str,
    db: Session = Depends(get_db)
):
    """
    Busca una zona por su código INE.

    URL:
        GET /zonas/cod-ine/28079

    Es útil porque cod_ine es único en el modelo Zona.
    """

    zona = crud.obtener_zona_por_cod_ine(db=db, cod_ine=cod_ine)

    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ninguna zona con cod_ine {cod_ine}"
        )

    return zona


@router.get("/{zona_id}", response_model=ZonaResponse)
def obtener_zona_por_id(
    zona_id: int,
    db: Session = Depends(get_db)
):
    """
    Busca una zona por su id.

    URL:
        GET /zonas/1
    """

    zona = crud.obtener_zona_por_id(db=db, zona_id=zona_id)

    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ninguna zona con id {zona_id}"
        )

    return zona


@router.post(
    "/",
    response_model=ZonaResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_zona(
    zona: ZonaCrear,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva zona.

    URL:
        POST /zonas/

    Antes de crearla, comprobamos si ya existe una zona con el mismo cod_ine.
    Esto evita chocar contra la restricción unique=True del modelo.
    """

    zona_existente = crud.obtener_zona_por_cod_ine(
        db=db,
        cod_ine=zona.cod_ine
    )

    if zona_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una zona con cod_ine {zona.cod_ine}"
        )

    # Convertimos el schema Pydantic a diccionario porque crud.crear_zona()
    # espera recibir zona_data como dict.
    zona_data = zona.model_dump()

    return crud.crear_zona(db=db, zona_data=zona_data)


@router.patch("/{zona_id}", response_model=ZonaResponse)
def actualizar_zona(
    zona_id: int,
    zona: ZonaActualizar,
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente una zona.

    URL:
        PATCH /zonas/1

    Solo se modifican los campos que mandes en el body.
    """

    zona_actual = crud.obtener_zona_por_id(db=db, zona_id=zona_id)

    if zona_actual is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ninguna zona con id {zona_id}"
        )

    # exclude_unset=True hace que solo pasen los campos enviados.
    zona_data = zona.model_dump(exclude_unset=True)

    # Si se quiere cambiar el cod_ine, comprobamos que no esté usado por otra zona.
    if "cod_ine" in zona_data:
        zona_con_mismo_cod_ine = crud.obtener_zona_por_cod_ine(
            db=db,
            cod_ine=zona_data["cod_ine"]
        )

        if (
            zona_con_mismo_cod_ine
            and zona_con_mismo_cod_ine.id != zona_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra zona con cod_ine {zona_data['cod_ine']}"
            )

    zona_actualizada = crud.actualizar_zona(
        db=db,
        zona_id=zona_id,
        zona_data=zona_data
    )

    return zona_actualizada


@router.delete("/{zona_id}")
def eliminar_zona(
    zona_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una zona por id.

    URL:
        DELETE /zonas/1

    En models.py tienes cascade='all, delete-orphan',
    así que si se elimina una zona, se eliminan también sus mediciones asociadas.
    """

    zona_eliminada = crud.eliminar_zona(db=db, zona_id=zona_id)

    if zona_eliminada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ninguna zona con id {zona_id}"
        )

    return {
        "message": "Zona eliminada correctamente",
        "zona_id": zona_id
    }
