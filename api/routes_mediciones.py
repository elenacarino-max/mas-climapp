# api/routes_mediciones.py

"""
Rutas API para gestionar mediciones climáticas.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import crud
<<<<<<< Updated upstream
=======
from db.database import get_db
>>>>>>> Stashed changes
from schemas.measurement_schema import (
    MedicionActualizar,
    MedicionCrear,
    MedicionRespuesta,
)

# El patrón de este archivo es muy similar al de routes_zonas.py, pero adaptado a las mediciones.
router = APIRouter(
    prefix="/mediciones",
    tags=["Mediciones"],
)


@router.get("/", response_model=list[MedicionRespuesta])
def listar_mediciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.obtener_mediciones(
        db=db,
        skip=skip,
        limit=limit,
    )


@router.get("/{medicion_id}", response_model=MedicionRespuesta)
def obtener_medicion(
    medicion_id: int,
    db: Session = Depends(get_db),
):
    medicion = crud.obtener_medicion_por_id(
        db=db,
        medicion_id=medicion_id,
    )

    if medicion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la medición con id {medicion_id}",
        )

    return medicion


@router.post(
    "/",
    response_model=MedicionRespuesta,
<<<<<<< Updated upstream
    status_code=status.HTTP_201_CREATED
=======
    status_code=status.HTTP_201_CREATED,
>>>>>>> Stashed changes
)
def crear_medicion(
    medicion: MedicionCrear,
    db: Session = Depends(get_db),
):
    medicion_data = medicion.model_dump()
    zona_id = medicion_data.pop("zona_id")

    nueva_medicion = crud.crear_medicion(
        db=db,
        medicion_data=medicion_data,
        zona_id=zona_id,
    )

    if nueva_medicion is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la medición",
        )

    return nueva_medicion


@router.patch("/{medicion_id}", response_model=MedicionRespuesta)
def actualizar_medicion(
    medicion_id: int,
    medicion: MedicionActualizar,
    db: Session = Depends(get_db),
):
    medicion_data = medicion.model_dump(exclude_unset=True)

    medicion_actualizada = crud.actualizar_medicion(
        db=db,
        medicion_id=medicion_id,
        medicion_data=medicion_data,
    )

    if medicion_actualizada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la medición con id {medicion_id}",
        )

    return medicion_actualizada


@router.delete("/{medicion_id}")
def eliminar_medicion(
    medicion_id: int,
    db: Session = Depends(get_db),
):
    medicion_eliminada = crud.eliminar_medicion(
        db=db,
        medicion_id=medicion_id,
    )

    if medicion_eliminada is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe la medición con id {medicion_id}",
        )

    return {
        "message": "Medición eliminada correctamente",
<<<<<<< Updated upstream
        "medicion_id": medicion_id
=======
        "medicion_id": medicion_id,
>>>>>>> Stashed changes
    }
