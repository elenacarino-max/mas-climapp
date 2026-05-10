# Importamos BaseModel para crear los schemas (estructuras de datos)
# y field_validator para validar automáticamente los campos
from pydantic import BaseModel, field_validator

# Importamos las funciones de validación que ya existen en el proyecto
# IMPORTANTE: estas funciones devuelven True o False
from utils.validators import (
    validar_temperatura,
    validar_humedad,
    validar_viento,
    validar_lluvia,
)


# ==========================================================
# CLASE BASE
# ==========================================================
# Aquí definimos los campos comunes a una medición
# Se reutiliza tanto en entrada como en salida
class MeasurementBase(BaseModel):

    # Temperatura registrada (número decimal)
    temperatura: float

    # Humedad registrada (número decimal)
    humedad: float

    # Velocidad del viento (número decimal)
    viento: float

    # Cantidad de lluvia (número decimal)
    lluvia: float


# ==========================================================
# SCHEMA DE ENTRADA (CREATE)
# ==========================================================
# Representa los datos que envía el usuario a la API
class MeasurementCreate(MeasurementBase):

    # ID de la estación meteorológica
    # El usuario lo envía para indicar de dónde es la medición
    estacion_id: int


    # ------------------------------------------------------
    # VALIDACIÓN DEL ID DE ESTACIÓN
    # ------------------------------------------------------
    @field_validator("estacion_id")
    @classmethod
    def check_estacion_id(cls, value):
        # Comprobamos que el ID sea positivo
        if value <= 0:
            raise ValueError("El ID de estación debe ser mayor que 0")
        return value


    # ------------------------------------------------------
    # VALIDACIÓN DE TEMPERATURA
    # ------------------------------------------------------
    @field_validator("temperatura")
    @classmethod
    def check_temperatura(cls, value):

        # Llamamos a la función existente que devuelve True o False
        if not validar_temperatura(value):
            raise ValueError("La temperatura debe estar entre -50 y 60 grados")

        # Si es válida, devolvemos el valor original
        return value


    # ------------------------------------------------------
    # VALIDACIÓN DE HUMEDAD
    # ------------------------------------------------------
    @field_validator("humedad")
    @classmethod
    def check_humedad(cls, value):

        if not validar_humedad(value):
            raise ValueError("La humedad debe estar entre 0 y 100")

        return value


    # ------------------------------------------------------
    # VALIDACIÓN DE VIENTO
    # ------------------------------------------------------
    @field_validator("viento")
    @classmethod
    def check_viento(cls, value):

        if not validar_viento(value):
            raise ValueError("El viento debe ser mayor o igual que 0")

        return value


    # ------------------------------------------------------
    # VALIDACIÓN DE LLUVIA
    # ------------------------------------------------------
    @field_validator("lluvia")
    @classmethod
    def check_lluvia(cls, value):

        if not validar_lluvia(value):
            raise ValueError("La lluvia debe ser mayor o igual que 0")

        return value


# ==========================================================
# SCHEMA DE SALIDA (RESPONSE)
# ==========================================================
# Representa los datos que devuelve la API
class MeasurementResponse(MeasurementBase):

    # Devolvemos también la estación asociada
    estacion_id: int

    # La fecha NO la envía el usuario, la genera el sistema
    fecha: str