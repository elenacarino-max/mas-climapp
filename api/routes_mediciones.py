# api/routes_mediciones.py

"""
Rutas API para gestionar mediciones climáticas.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud

# El patrón de este archivo es muy similar al de routes_zonas.py, pero adaptado a las mediciones.
router = APIRouter(
    prefix="/mediciones",
    tags=["Mediciones"]
)


class MedicionBase(BaseModel):
    fecha_datos: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    viento: Optional[float] = None
    lluvia: Optional[float] = None


class MedicionCrear(BaseModel):
    zona_id: int
    fecha_datos: str
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    viento: Optional[float] = None
    lluvia: Optional[float] = None


class MedicionActualizar(BaseModel):
    fecha_datos: Optional[str] = None
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    viento: Optional[float] = None
    lluvia: Optional[float] = None


class MedicionResponse(MedicionBase):
    id: int
    zona_id: int

    model_config = ConfigDict(from_attributes=True)


@router.get("/", response_model=list[MedicionResponse])
def listar_mediciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.obtener_mediciones(
        db=db,
        skip=skip,
        limit=limit
    )


@router.get("/{medicion_id}", response_model=MedicionResponse)
def obtener_medicion(
    medicion_id: int,
    db: Session = Depends(get_db)
):
    medicion = crud.obtener_medicion_por_id(
        db=db,
        medicion_id=medicion_id
    )

    if medicion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la medición con id {medicion_id}"
        )

    return medicion


@router.post(
    "/",
    response_model=MedicionResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_medicion(
    medicion: MedicionCrear,
    db: Session = Depends(get_db)
):
    medicion_data = medicion.model_dump()

    zona_id = medicion_data.pop("zona_id")

    nueva_medicion = crud.MedicionCrear(
        db=db,
        medicion_data=medicion_data,
        zona_id=zona_id
    )

    if nueva_medicion is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la medición"
        )

    return nueva_medicion


@router.patch("/{medicion_id}", response_model=MedicionResponse)
def actualizar_medicion(
    medicion_id: int,
    medicion: MedicionActualizar,
    db: Session = Depends(get_db)
):
    medicion_data = medicion.model_dump(exclude_unset=True)

    medicion_actualizada = crud.MedicionActualizar(
        db=db,
        medicion_id=medicion_id,
        medicion_data=medicion_data
    )

    if medicion_actualizada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la medición con id {medicion_id}"
        )

    return medicion_actualizada


@router.delete("/{medicion_id}")
def eliminar_medicion(
    medicion_id: int,
    db: Session = Depends(get_db)
):
    medicion_eliminada = crud.eliminar_medicion(
        db=db,
        medicion_id=medicion_id
    )

    if medicion_eliminada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la medición con id {medicion_id}"
        )

    return {
        "message": "Medición eliminada correctamente",
        "medicion_id": medicion_id
    }