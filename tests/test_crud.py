##test CRUD de al base de datos
## CRUD = Create, Read, Update, Delete
# Los test comprueban: 
# Que las tablas funcionan correctamente
# Los datos se insertan bien
# Se pueden consultar
# Se pueden modificar
# Se pueden borrar  
# Las restricciones de integridad funcionan

import pytest

# create_engine → crea conexión con SQLite
# inspect → inspecciona tablas de la BD
from sqlalchemy import create_engine, inspect

# sessionmaker → crea sesiones SQLAlchemy
from sqlalchemy.orm import sessionmaker

# Base → contiene metadata de las tablas
# create_tables → función que crea tablas
from db.database import Base, create_tables

# Modelos ORM
from db.models import Zona, Medicion

# Se crea una BD SQLite temporal en RAM. Cada test empieza limpio y no toca clima.db. 
# Los test no afectan entre sí y son más rápidos que usar la BD real. Al finalizar cada test, se cierra la sesión y se destruyen las tablas.

@pytest.fixture
def db():
    # Crear BD SQLite en RAM
    engine = create_engine("sqlite:///:memory:")

    # Crear todas tablas definidas en Base
    Base.metadata.create_all(bind=engine)

    # Crear clase sesión conectada al engine
    Session = sessionmaker(bind=engine)

    # Crear sesión
    session = Session()

    # Test sesión
    yield session

    # Cerrar conexión y destruir tablas
    session.close()
    Base.metadata.drop_all(bind=engine)


# C = CREATE -> crear registros en la BD / INSERT funciona correctamente

def test_create_zona(db): # Crear una zona y verificar que se guarda bien.

    # Crear objeto zona
    zona = Zona(
        municipio="Madrid",
        cod_ine="28079",
        id_estacion="3195",
        estacion_referencia="Retiro"
    )

    # Insertar en BD
    db.add(zona)    # Añade le objeto a la sesión
    db.commit()     # Inserta el registro en la BD (INSERT)

    # Comprobar que el dato se ha guardado y existe (Assert)
    resultado = db.query(Zona).filter_by(cod_ine="28079").first()

    assert resultado is not None
    assert resultado.municipio == "Madrid"


def test_create_medicion(db): # Crear una medición y verificar que se guarda bien.

    # Crear objeto zona
    zona = Zona(
        municipio="Madrid",
        cod_ine="28079",
        id_estacion="3195",
        estacion_referencia="Retiro"
    )

    # Insertar en BD
    db.add(zona)
    db.commit()

    # Crear medición asociada a la zona
    medicion = Medicion(
        zona_id=zona.id,
        fecha_datos="2024-06-15",
        temperatura=22.0
    )

    # Insertar en BD
    db.add(medicion)
    db.commit()

    # Comprobar que el dato se ha guardado y existe (Assert)
    resultado = db.query(Medicion).first()

    assert resultado is not None
    assert resultado.temperatura == 22.0


# R = READ -> leer registros de la BD / SELECT funciona correctamente

def test_read_zona(db): # Verifica que se puede leer una zona.

    # Crear objeto zona
    zona = Zona(
        municipio="Barcelona",
        cod_ine="08019",
        id_estacion="1234",
        estacion_referencia="Centro"
    )

    # Insertar en BD
    db.add(zona)
    db.commit()

    # Consulta SELECT para leer la zona por su cod_ine
    resultado = db.query(Zona).filter_by(cod_ine="08019").first()

    # Verificar que se ha leído correctamente
    assert resultado is not None
    assert resultado.municipio == "Barcelona"


def test_read_mediciones_relacion(db): # Verifica la relación Zona → Mediciones.
    
    # Crear objeto zona
    zona = Zona(
        municipio="Sevilla",
        cod_ine="41091",
        id_estacion="8888",
        estacion_referencia="Sur"
    )
    # Insertar en BD
    db.add(zona)
    db.commit()

    # Crear objeto medición 1 asociado a la zona
    m1 = Medicion(
        zona_id=zona.id,
        fecha_datos="2024-06-15",
        temperatura=30.0
    )
    # Crear objeto medición 2 asociado a la zona
    m2 = Medicion(
        zona_id=zona.id,
        fecha_datos="2024-06-16",
        temperatura=31.5
    )

    # Insertar en BD
    db.add_all([m1, m2])
    db.commit()

    # Recarga el objeto desde la BD para asegurarse de que las relaciones están actualizadas
    db.refresh(zona)

    # Comprobar que la zona tiene 2 mediciones asociadas
    assert len(zona.mediciones) == 2


# U = UPDATE -> Actualizar registros de la BD / UPDATE funciona correctamente


def test_update_zona(db): # Verifica que una zona puede actualizarse.

    # Crear objeto zona
    zona = Zona(
        municipio="Valencia",
        cod_ine="46250",
        id_estacion="5555",
        estacion_referencia="Norte"
    )
    # Insertar en BD
    db.add(zona)
    db.commit()

    # Cambiar municipio del objeto zona
    zona.municipio = "Valencia Capital"

    # Guardar / Actualizar en BD
    db.commit()

    # Leer de nuevo
    resultado = db.query(Zona).filter_by(cod_ine="46250").first()

    # Verificar actualización
    assert resultado.municipio == "Valencia Capital"


def test_update_medicion(db): # Verifica que una medición puede actualizarse.

    # Crear objeto zona
    zona = Zona(
        municipio="Bilbao",
        cod_ine="48020",
        id_estacion="9999",
        estacion_referencia="Aeropuerto"
    )
    # Insertar en BD
    db.add(zona)
    db.commit()
    # Crear objeto zona
    medicion = Medicion(
        zona_id=zona.id,
        fecha_datos="2024-06-15",
        temperatura=18.0
    )
    # Insertar en BD
    db.add(medicion)
    db.commit()

    # Actualizar temperatura del objeto medición 
    medicion.temperatura = 20.5
    #Guardar UPDATE en BD
    db.commit()

    # Leer de nuevo
    resultado = db.query(Medicion).first()
    # Verificar actualización
    assert resultado.temperatura == 20.5


# D = DELETE -> Eliminar registros de la BD / DELETE funciona correctamente

def test_delete_medicion(db):  # Verifica que una medición puede borrarse.

    # Crear zona y medición asociada
    zona = Zona(
        municipio="Málaga",
        cod_ine="29067",
        id_estacion="4444",
        estacion_referencia="Puerto"
    )

    db.add(zona)
    db.commit()

    medicion = Medicion(
        zona_id=zona.id,
        fecha_datos="2024-06-15",
        temperatura=27.0
    )

    db.add(medicion)
    db.commit()

    # Borrar medición de la BD
    db.delete(medicion)     # Marca el objeto para borrado
    db.commit()             # Ejecuta el DELETE en la BD

    # Verifcar que Medicion ya no existe
    resultado = db.query(Medicion).all()

    assert resultado == []


def test_delete_zona_cascade(db):   # Borrado en cascada -> Verifica que al borrar una zona también se borran sus mediciones.
    
    # Crear zona y medición asociada
    zona = Zona(
        municipio="Granada",
        cod_ine="18087",
        id_estacion="7777",
        estacion_referencia="Centro"
    )

    db.add(zona)
    db.commit()

    medicion = Medicion(
        zona_id=zona.id,
        fecha_datos="2024-06-15",
        temperatura=24.0
    )

    db.add(medicion)
    db.commit()

    # Borrar zona de la BD (debería borrar también la medición por cascada)
    db.delete(zona)
    db.commit()

    # Verifcar que no existe la medición asociada a la zona
    resultado = db.query(Medicion).filter_by(zona_id=zona.id).all()

    assert resultado == []


# TESTS DE INTEGRIDAD

def test_cod_ine_unico(db):     # Verificar que no existen dos zonas con el mismo cod_ine.
    
    # Crear dos zonas con el mismo cod_ine
    zona1 = Zona(
        municipio="Madrid",
        cod_ine="28079",
        id_estacion="3195",
        estacion_referencia="Retiro"
    )

    zona2 = Zona(
        municipio="Otro Madrid",
        cod_ine="28079",  # repetido
        id_estacion="9999",
        estacion_referencia="Otra"
    )

    # Insertar la primera zona funciona bien
    db.add(zona1)
    db.commit()

    with pytest.raises(Exception):
        # Intentar insertar la segunda zona con cod_ine repetido debería devolver excepción (error de integridad)
        db.add(zona2)
        db.commit()


def test_medicion_sin_zona_falla(db):   # No se puede insertar una medición con una zona inexistente.
    
    # Crear medición con zona_id que no existe en la tabla Zona
    medicion = Medicion(
        zona_id=999,
        fecha_datos="2024-06-15",
        temperatura=20.0
    )

    # Debe fallar al intentar insertar la medición porque zona_id=999 no existe en la tabla Zona (violación de clave foránea)
    with pytest.raises(Exception):
        db.add(medicion)
        db.commit()


def test_create_tables_idempotente():   # create_tables() puede ejecutarse varias veces sin romper nada.

    # Ejecutar la creación de tablas varias veces. No debería dar error ni crear tablas duplicadas.
    create_tables()
    create_tables()


def test_created_at_automatico(db): # Verificar que SQLAlchemy rellena automáticamente el campo created_at.

    # Crear objeto Zona
    zona = Zona(
        municipio="Madrid",
        cod_ine="28079",
        id_estacion="3195",
        estacion_referencia="Retiro"
    )

    db.add(zona)
    db.commit()

    # Crear medición SIN pasar created_at
    medicion = Medicion(
        zona_id=zona.id,
        fecha_datos="2024-06-15",
        temperatura=22.0
    )

    db.add(medicion)
    db.commit()

    # Verificar que created_at se ha rellenado automáticamente
    assert medicion.created_at is not None