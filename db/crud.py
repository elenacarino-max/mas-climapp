from sqlalchemy.orm import Session
from db import models

# OPERACIONES PARA ZONAS

def obtener_zona_por_codigo(db: Session, cod_ine: str):
    """Busca una zona por su código INE para evitar duplicados."""
    return db.query(models.Zona).filter(models.Zona.cod_ine == cod_ine).first()

def crear_zona(db: Session, municipio: str, cod_ine: str, id_estacion: str, estacion_referencia: str):
    """Crea una nueva zona en la base de datos."""
    db_zona = models.Zona(
        municipio=municipio,
        cod_ine=cod_ine,
        id_estacion=id_estacion,
        estacion_referencia=estacion_referencia
    )
    db.add(db_zona)
    db.commit()
    db.refresh(db_zona)
    return db_zona

# OPERACIONES PARA MEDICIONES

def crear_medicion(db: Session, medicion_data: dict, zona_id: int):
    """
    Crea una medición vinculada a una zona.
    Usa 'fecha_datos' para coincidir con el modelo de Gianmario.
    """
    db_medicion = models.Medicion(
        zona_id=zona_id,
        fecha_datos=medicion_data.get("fecha"),
        temperatura=medicion_data.get("temperatura"),
        humedad=medicion_data.get("humedad"),
        viento=medicion_data.get("viento"),
        lluvia=medicion_data.get("lluvia"),
        presion=medicion_data.get("presion")
    )
    db.add(db_medicion)
    db.commit()
    db.refresh(db_medicion)
    return db_medicion

def obtener_mediciones(db: Session, skip: int = 0, limit: int = 100):
    """Lista las mediciones con paginación."""
    return db.query(models.Medicion).offset(skip).limit(limit).all()