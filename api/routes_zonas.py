# =====================================================
# FUNCIONES DE ZONAS
# =====================================================

from sqlalchemy.orm import Session
from . import models


def obtener_zonas(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista de zonas desde la base de datos.

    Parámetros:
    - db: sesión activa de SQLAlchemy.
    - skip: número de registros a saltar.
    - limit: número máximo de registros a devolver.

    Devuelve:
    - Lista de zonas.
    """

    return db.query(models.Zona).offset(skip).limit(limit).all()


def obtener_zona_por_id(db: Session, zona_id: int):
    """
    Busca una zona concreta por su ID.

    Parámetros:
    - db: sesión activa de SQLAlchemy.
    - zona_id: ID de la zona a buscar.

    Devuelve:
    - La zona si existe.
    - None si no existe.
    """

    return db.query(models.Zona).filter(
        models.Zona.id == zona_id
    ).first()


def obtener_zona_por_cod_ine(db: Session, cod_ine: str):
    """
    Busca una zona usando su código INE.

    Parámetros:
    - db: sesión activa de SQLAlchemy.
    - cod_ine: código INE del municipio.

    Devuelve:
    - La zona si existe.
    - None si no existe.
    """

    return db.query(models.Zona).filter(
        models.Zona.cod_ine == cod_ine
    ).first()


def ZonaCrear(db: Session, zona_data: dict):
    """
    Crea una nueva zona en la base de datos.

    Antes de crearla:
    - comprueba si ya existe una zona con el mismo cod_ine
    - evita duplicados

    Parámetros:
    - db: sesión activa de SQLAlchemy.
    - zona_data: diccionario con los datos de la zona.

    Devuelve:
    - La zona creada.
    - La zona existente si ya estaba creada.
    """

    # Evitar duplicados por cod_ine
    db_zona = obtener_zona_por_cod_ine(
        db,
        cod_ine=zona_data.get("cod_ine")
    )

    if db_zona:
        return db_zona

    # Crear nueva zona
    nueva_zona = models.Zona(
        municipio=zona_data.get("municipio"),
        cod_ine=zona_data.get("cod_ine"),
        id_estacion=zona_data.get("id_estacion"),
        estacion_referencia=zona_data.get("estacion_referencia")
    )

    # INSERT en base de datos
    db.add(nueva_zona)
    db.commit()
    db.refresh(nueva_zona)

    return nueva_zona


def ZonaActualizar(
    db: Session,
    zona_id: int,
    zona_data: dict,
):
    """
    Actualiza una zona existente.

    Parámetros:
    - db: sesión activa de SQLAlchemy.
    - zona_id: ID de la zona a modificar.
    - zona_data: nuevos datos de la zona.

    Devuelve:
    - Zona actualizada.
    - None si no existe.
    """

    db_zona = obtener_zona_por_id(db, zona_id)

    if not db_zona:
        return None

    # Actualización manual segura
    if "municipio" in zona_data:
        db_zona.municipio = zona_data["municipio"]

    if "cod_ine" in zona_data:
        db_zona.cod_ine = zona_data["cod_ine"]

    if "id_estacion" in zona_data:
        db_zona.id_estacion = zona_data["id_estacion"]

    if "estacion_referencia" in zona_data:
        db_zona.estacion_referencia = zona_data[
            "estacion_referencia"
        ]

    # UPDATE en base de datos
    db.commit()
    db.refresh(db_zona)

    return db_zona


def eliminar_zona(db: Session, zona_id: int):
    """
    Elimina una zona de la base de datos.

    Parámetros:
    - db: sesión activa de SQLAlchemy.
    - zona_id: ID de la zona a eliminar.

    Devuelve:
    - Zona eliminada.
    - None si no existe.
    """

    db_zona = obtener_zona_por_id(db, zona_id)

    if db_zona:
        db.delete(db_zona)
        db.commit()

    return db_zona