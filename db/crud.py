from sqlalchemy.orm import Session
from db import models

# OPERACIONES DE ZONAS

def obtener_zona_por_id(db: Session, zona_id: int):
    return db.query(models.Zona).filter(models.Zona.id == zona_id).first()

def obtener_zona_por_codigo(db: Session, cod_ine: str):
    return db.query(models.Zona).filter(models.Zona.cod_ine == cod_ine).first()

def obtener_zonas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Zona).offset(skip).limit(limit).all()

def crear_zona(db: Session, municipio: str, cod_ine: str, id_estacion: int, estacion_referencia: str):
    # Verificamos si ya existe
    db_zona = obtener_zona_por_codigo(db, cod_ine=cod_ine)
    if db_zona:
        return db_zona
    
    nueva_zona = models.Zona(
        municipio=municipio,
        cod_ine=cod_ine,
        id_estacion=id_estacion,
        estacion_referencia=estacion_referencia
    )
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)
    return nueva_zona

# OPERACIONES DE MEDICIONES

def obtener_medicion_por_id(db: Session, medicion_id: int):
    return db.query(models.Medicion).filter(models.Medicion.id == medicion_id).first()

def crear_medicion(db: Session, medicion_data: dict, zona_id: int):
    # Aplicamos la flexibilidad en la fecha
    fecha = medicion_data.get("fecha_datos") or medicion_data.get("fecha")
    
    nueva_medicion = models.Medicion(
        zona_id=zona_id,
        fecha_datos=fecha,
        temperatura_max=medicion_data.get("temperatura_max"),
        temperatura_min=medicion_data.get("temperatura_min"),
        precipitacion=medicion_data.get("precipitacion")
    )
    db.add(nueva_medicion)
    db.commit()
    db.refresh(nueva_medicion)
    return nueva_medicion

def actualizar_medicion(db: Session, medicion_id: int, updates: dict):
    db_medicion = obtener_medicion_por_id(db, medicion_id)
    if db_medicion:
        for key, value in updates.items():
            setattr(db_medicion, key, value)
        db.commit()
        db.refresh(db_medicion)
    return db_medicion

def eliminar_medicion(db: Session, medicion_id: int):
    db_medicion = obtener_medicion_por_id(db, medicion_id)
    if db_medicion:
        db.delete(db_medicion)
        db.commit()
        return True
    return False