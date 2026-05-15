from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from db.models import Medicion, Zona


def obtener_zonas(db: Session, skip: int = 0, limit: int = 100) -> List[Zona]:
    return db.query(Zona).offset(skip).limit(limit).all()


def obtener_zona_por_id(db: Session, zona_id: int) -> Optional[Zona]:
    return db.query(Zona).filter(Zona.id == zona_id).first()


def obtener_zona_por_cod_ine(db: Session, cod_ine: str) -> Optional[Zona]:
    return db.query(Zona).filter(Zona.cod_ine == cod_ine).first()


def crear_zona(db: Session, zona_data: Dict[str, Any]) -> Zona:
    zona = Zona(**zona_data)
    db.add(zona)
    db.commit()
    db.refresh(zona)
    return zona


def actualizar_zona(
    db: Session,
    zona_id: int,
    zona_data: Dict[str, Any],
) -> Optional[Zona]:
    zona = obtener_zona_por_id(db=db, zona_id=zona_id)

    if zona is None:
        return None

    for campo, valor in zona_data.items():
        setattr(zona, campo, valor)

    db.commit()
    db.refresh(zona)
    return zona


def eliminar_zona(db: Session, zona_id: int) -> Optional[Zona]:
    zona = obtener_zona_por_id(db=db, zona_id=zona_id)

    if zona is None:
        return None

    db.delete(zona)
    db.commit()
    return zona


def obtener_mediciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Medicion]:
    return db.query(Medicion).offset(skip).limit(limit).all()


def obtener_medicion_por_id(
    db: Session,
    medicion_id: int,
) -> Optional[Medicion]:
    return db.query(Medicion).filter(Medicion.id == medicion_id).first()


def crear_medicion(
    db: Session,
    medicion_data: Dict[str, Any],
    zona_id: Optional[int] = None,
) -> Optional[Medicion]:
    if zona_id is None:
        zona_id = medicion_data.get("zona_id")

    if zona_id is None or obtener_zona_por_id(db=db, zona_id=zona_id) is None:
        return None

    datos = {**medicion_data, "zona_id": zona_id}
    medicion = Medicion(**datos)

    db.add(medicion)
    db.commit()
    db.refresh(medicion)
    return medicion


def actualizar_medicion(
    db: Session,
    medicion_id: int,
    medicion_data: Dict[str, Any],
) -> Optional[Medicion]:
    medicion = obtener_medicion_por_id(db=db, medicion_id=medicion_id)

    if medicion is None:
        return None

    zona_id = medicion_data.get("zona_id")
    if zona_id is not None and obtener_zona_por_id(db=db, zona_id=zona_id) is None:
        return None

    for campo, valor in medicion_data.items():
        setattr(medicion, campo, valor)

    db.commit()
    db.refresh(medicion)
    return medicion


def eliminar_medicion(db: Session, medicion_id: int) -> Optional[Medicion]:
    medicion = obtener_medicion_por_id(db=db, medicion_id=medicion_id)

    if medicion is None:
        return None

    db.delete(medicion)
    db.commit()
    return medicion
