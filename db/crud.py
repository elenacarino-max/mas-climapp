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
    
    # Mapeo explícito en lugar de **zona_data para evitar fallos
    nueva_zona = models.Zona(
        municipio=zona_data.get("municipio"),
        cod_ine=zona_data.get("cod_ine"),
        id_estacion=zona_data.get("id_estacion"),
        estacion_referencia=zona_data.get("estacion_referencia")
    )
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)
    return nueva_zona

def actualizar_zona(db: Session, zona_id: int, zona_data: dict):
    db_zona = obtener_zona_por_id(db, zona_id)
    if db_zona:
        # Mapeo seguro para no meter campos inexistentes
        if "municipio" in zona_data: db_zona.municipio = zona_data["municipio"]
        if "cod_ine" in zona_data: db_zona.cod_ine = zona_data["cod_ine"]
        if "id_estacion" in zona_data: db_zona.id_estacion = zona_data["id_estacion"]
        if "estacion_referencia" in zona_data: db_zona.estacion_referencia = zona_data["estacion_referencia"]
        
        db.commit()
        db.refresh(db_zona)
    return db_zona

def eliminar_zona(db: Session, zona_id: int):
    db_zona = obtener_zona_por_id(db, zona_id)
    if db_zona:
        db.delete(db_zona)
        db.commit()
    return db_zona


# FUNCIONES DE MEDICIONES

def obtener_mediciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Medicion).offset(skip).limit(limit).all()

# Función nueva necesaria para la API
def obtener_medicion_por_id(db: Session, medicion_id: int):
    return db.query(models.Medicion).filter(models.Medicion.id == medicion_id).first()

def crear_medicion(db: Session, medicion_data: dict, zona_id: int):
    # Lógica de resolución de nombres (temperatura, lluvia, fecha)
    temp = medicion_data.get("temperatura")
    if temp is None:
        temp = medicion_data.get("temperatura_max")
        
    # Usamos 'lluvia' que es el nombre en models.py
    precip = medicion_data.get("lluvia")
    if precip is None:
        precip = medicion_data.get("precipitacion")

    fecha = medicion_data.get("fecha_datos") or medicion_data.get("fecha")
    
    if fecha is None:
        return None

    # Mapeo explícito y campos extra (humedad, viento)
    nueva_medicion = models.Medicion(
        zona_id=zona_id,
        fecha_datos=fecha,
        temperatura=temp,
        lluvia=precip,
        humedad=medicion_data.get("humedad"),
        viento=medicion_data.get("viento")
        # 'presion' no se incluye porque confirmamos que no está en models.py
    )
    db.add(nueva_medicion)
    db.commit()
    db.refresh(nueva_medicion)
    return nueva_medicion

def actualizar_medicion(db: Session, medicion_id: int, medicion_data: dict):
    db_medicion = obtener_medicion_por_id(db, medicion_id)
    if not db_medicion:
        return None

    # Mapeo manual para evitar el riesgo de setattr() con basura
    if "temperatura" in medicion_data or "temperatura_max" in medicion_data:
        db_medicion.temperatura = medicion_data.get("temperatura") or medicion_data.get("temperatura_max")
    
    if "lluvia" in medicion_data or "precipitacion" in medicion_data:
        db_medicion.lluvia = medicion_data.get("lluvia") or medicion_data.get("precipitacion")

    if "humedad" in medicion_data:
        db_medicion.humedad = medicion_data["humedad"]
    
    if "viento" in medicion_data:
        db_medicion.viento = medicion_data["viento"]

    if "fecha_datos" in medicion_data or "fecha" in medicion_data:
        db_medicion.fecha_datos = medicion_data.get("fecha_datos") or medicion_data.get("fecha")

    db.commit()
    db.refresh(db_medicion)
    return db_medicion

def eliminar_medicion(db: Session, medicion_id: int):
    db_medicion = obtener_medicion_por_id(db, medicion_id)
    if db_medicion:
        db.delete(db_medicion)
        db.commit()
    return db_medicion