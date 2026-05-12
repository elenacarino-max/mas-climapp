from sqlalchemy.orm import Session
from . import models

# FUNCIONES DE ZONA

def obtener_zonas(db: Session):
    return db.query(models.Zona).all()

def obtener_zona_por_id(db: Session, zona_id: int):
    return db.query(models.Zona).filter(models.Zona.id == zona_id).first()

def obtener_zona_por_codigo(db: Session, cod_ine: str):
    return db.query(models.Zona).filter(models.Zona.cod_ine == cod_ine).first()

def crear_zona(db: Session, municipio: str, cod_ine: str, id_estacion: str, estacion_referencia: str):
    # Check de duplicados
    db_zona = obtener_zona_por_codigo(db, cod_ine)
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

# FUNCIONES DE MEDICIÓN

def obtener_medicion_por_id(db: Session, medicion_id: int):
    return db.query(models.Medicion).filter(models.Medicion.id == medicion_id).first()

def crear_medicion(db: Session, medicion_data: dict, zona_id: int):
    # Flexibilidad de fecha (Elena)
    fecha = medicion_data.get("fecha_datos") or medicion_data.get("fecha")
    
    # Mapeo de campos reales del modelo
    # Usamos .get() con alternativas para que no falle use el nombre que use la API
    nueva_medicion = models.Medicion(
        zona_id=zona_id,
        fecha_datos=fecha,
        temperatura=medicion_data.get("temperatura") or medicion_data.get("temperatura_max"),
        lluvia=medicion_data.get("lluvia") or medicion_data.get("precipitacion"),
        humedad=medicion_data.get("humedad"),
        viento=medicion_data.get("viento")
    )
    # Se eliminan 'presion' y 'temperatura_min' porque no existen en models.py
    
    db.add(nueva_medicion)
    db.commit()
    db.refresh(nueva_medicion)
    return nueva_medicion

def actualizar_medicion(db: Session, medicion_id: int, medicion_data: dict):
    db_medicion = obtener_medicion_por_id(db, medicion_id)
    if db_medicion:
        # Actualizamos solo los campos que vienen en el diccionario
        if "temperatura" in medicion_data or "temperatura_max" in medicion_data:
            db_medicion.temperatura = medicion_data.get("temperatura") or medicion_data.get("temperatura_max")
        if "lluvia" in medicion_data or "precipitacion" in medicion_data:
            db_medicion.lluvia = medicion_data.get("lluvia") or medicion_data.get("precipitacion")
        
        db_medicion.humedad = medicion_data.get("humedad", db_medicion.humedad)
        db_medicion.viento = medicion_data.get("viento", db_medicion.viento)
        
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