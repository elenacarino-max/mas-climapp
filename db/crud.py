from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from db.models import Medicion, Zona


def _normalizar_fecha_datos(valor: Any) -> Optional[str]:
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor.date().isoformat()

    if isinstance(valor, date):
        return valor.isoformat()

    fecha = str(valor).strip()
    if not fecha:
        return None

    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(fecha[:19], formato).date().isoformat()
        except ValueError:
            continue

    return fecha


def obtener_zonas(db: Session, skip: int = 0, limit: int = 100) -> List[Zona]:
    return db.query(Zona).offset(skip).limit(limit).all()


def obtener_zona_por_id(db: Session, zona_id: int) -> Optional[Zona]:
    return db.query(Zona).filter(Zona.id == zona_id).first()


def obtener_zona_por_cod_ine(db: Session, cod_ine: str) -> Optional[Zona]:
    return db.query(Zona).filter(Zona.cod_ine == cod_ine).first()


def crear_zona(db: Session, zona_data: Dict[str, Any]) -> Zona:
    zona_existente = obtener_zona_por_cod_ine(
        db=db,
        cod_ine=zona_data.get("cod_ine"),
    )

    if zona_existente:
        return zona_existente

    zona = Zona(
        municipio=zona_data.get("municipio"),
        cod_ine=zona_data.get("cod_ine"),
        id_estacion=zona_data.get("id_estacion"),
        estacion_referencia=zona_data.get("estacion_referencia"),
    )

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

    campos_permitidos = {
        "municipio",
        "cod_ine",
        "id_estacion",
        "estacion_referencia",
    }

    for campo in campos_permitidos:
        if campo in zona_data:
            setattr(zona, campo, zona_data[campo])

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

    fecha_datos = _normalizar_fecha_datos(
        medicion_data.get("fecha_datos") or medicion_data.get("fecha")
    )

    if fecha_datos is None:
        return None

    medicion = Medicion(
        zona_id=zona_id,
        fecha_datos=fecha_datos,
        temperatura=(
            medicion_data.get("temperatura")
            if medicion_data.get("temperatura") is not None
            else medicion_data.get("temperatura_max")
        ),
        humedad=medicion_data.get("humedad"),
        viento=medicion_data.get("viento"),
        lluvia=(
            medicion_data.get("lluvia")
            if medicion_data.get("lluvia") is not None
            else medicion_data.get("precipitacion")
        ),
    )

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
    if zona_id is not None:
        if obtener_zona_por_id(db=db, zona_id=zona_id) is None:
            return None

        medicion.zona_id = zona_id

    if "temperatura" in medicion_data or "temperatura_max" in medicion_data:
        medicion.temperatura = (
            medicion_data.get("temperatura")
            if medicion_data.get("temperatura") is not None
            else medicion_data.get("temperatura_max")
        )

    if "humedad" in medicion_data:
        medicion.humedad = medicion_data["humedad"]

    if "viento" in medicion_data:
        medicion.viento = medicion_data["viento"]

    if "lluvia" in medicion_data or "precipitacion" in medicion_data:
        medicion.lluvia = (
            medicion_data.get("lluvia")
            if medicion_data.get("lluvia") is not None
            else medicion_data.get("precipitacion")
        )

    if "fecha_datos" in medicion_data or "fecha" in medicion_data:
        fecha_datos = _normalizar_fecha_datos(
            medicion_data.get("fecha_datos") or medicion_data.get("fecha")
        )

        if fecha_datos is None:
            return None

        medicion.fecha_datos = fecha_datos

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
