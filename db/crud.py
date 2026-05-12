from sqlalchemy.orm import Session
from . import models

# FUNCIONES DE ZONAS

def obtener_zonas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Zona).offset(skip).limit(limit).all()

def obtener_zona_por_id(db: Session, zona_id: int):
    return db.query(models.Zona).filter(models.Zona.id == zona_id).first()

def obtener_zona_por_cod_ine(db: Session, cod_ine: str):
    return db.query(models.Zona).filter(models.Zona.cod_ine == cod_ine).first()

def crear_zona(db: Session, zona_data: dict):
    # Evitar duplicados por cod_ine
    db_zona = obtener_zona_por_cod_ine(db, cod_ine=zona_data.get("cod_ine"))
    if db_zona:
        return db_zona
    
    nueva_zona = models.Zona(**zona_data)
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)
    return nueva_zona

def actualizar_zona(db: Session, zona_id: int, zona_data: dict):
    db_zona = db.query(models.Zona).filter(models.Zona.id == zona_id).first()
    if db_zona:
        for key, value in zona_data.items():
            setattr(db_zona, key, value)
        db.commit()
        db.refresh(db_zona)
    return db_zona

def eliminar_zona(db: Session, zona_id: int):
    db_zona = db.query(models.Zona).filter(models.Zona.id == zona_id).first()
    if db_zona:
        db.delete(db_zona)
        db.commit()
    return db_zona


# FUNCIONES DE MEDICIONES

def obtener_mediciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Medicion).offset(skip).limit(limit).all()

def crear_medicion(db: Session, medicion_data: dict, zona_id: int):
    # Lógica segura para valores 0 y mapeo de campos evitando el error del 'or'
    temp = medicion_data.get("temperatura")
    if temp is None:
        temp = medicion_data.get("temperatura_max")
        
    precip = medicion_data.get("precipitacion")
    if precip is None:
        precip = medicion_data.get("lluvia")

    # Manejo de fecha
    fecha = medicion_data.get("fecha_datos")
    if fecha is None:
        fecha = medicion_data.get("fecha")
    
    if fecha is None:
        # Si no hay fecha en ningún campo, no podemos crear la medición
        return None

    nueva_medicion = models.Medicion(
        zona_id=zona_id,
        fecha_datos=fecha,
        temperatura=temp,
        precipitacion=precip
        # 'presion' no se incluye porque no existe en models.py
    )
    db.add(nueva_medicion)
    db.commit()
    db.refresh(nueva_medicion)
    return nueva_medicion

def actualizar_medicion(db: Session, medicion_id: int, medicion_data: dict):
    db_medicion = db.query(models.Medicion).filter(models.Medicion.id == medicion_id).first()
    if db_medicion:
        for key, value in medicion_data.items():
            setattr(db_medicion, key, value)
        db.commit()
        db.refresh(db_medicion)
    return db_medicion

def eliminar_medicion(db: Session, medicion_id: int):
    db_medicion = db.query(models.Medicion).filter(models.Medicion.id == medicion_id).first()
    if db_medicion:
        db.delete(db_medicion)
        db.commit()
    return db_medicion