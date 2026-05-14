# api/routes_zonas.py

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud

# El patrón de este archivo es muy similar al de routes_mediciones.py, pero adaptado a las zonas.
router = APIRouter(
    prefix="/zonas",
    tags=["Zonas"]
)


class ZonaBase(BaseModel):
    municipio: str
    cod_ine: str
    id_estacion: str
    estacion_referencia: str


class ZonaCrear(ZonaBase):
    pass


class ZonaActualizar(BaseModel):
    municipio: Optional[str] = None
    cod_ine: Optional[str] = None
    id_estacion: Optional[str] = None
    estacion_referencia: Optional[str] = None


class ZonaResponse(ZonaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


@router.get("/", response_model=list[ZonaResponse])
def listar_zonas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud.obtener_zonas(db=db, skip=skip, limit=limit)


@router.get("/cod-ine/{cod_ine}", response_model=ZonaResponse)
def obtener_zona_por_cod_ine(
    cod_ine: str,
    db: Session = Depends(get_db)
):
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
    zona_existente = crud.obtener_zona_por_cod_ine(
        db=db,
        cod_ine=zona.cod_ine
    )

    if zona_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una zona con cod_ine {zona.cod_ine}"
        )

    zona_data = zona.model_dump()

    return crud.crear_zona(db=db, zona_data=zona_data)

# El patrón de este archivo es muy similar al de routes_mediciones.py, pero adaptado a las zonas.

@router.patch("/{zona_id}", response_model=ZonaResponse)
def actualizar_zona(
    zona_id: int,
    zona: ZonaActualizar,
    db: Session = Depends(get_db)
):
    zona_actual = crud.obtener_zona_por_id(db=db, zona_id=zona_id)

    if zona_actual is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ninguna zona con id {zona_id}"
        )

    zona_data = zona.model_dump(exclude_unset=True)

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