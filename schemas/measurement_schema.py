# Para manejar fechas reales (created_at) que vienen de la base de datos
from datetime import datetime  

# Importamos BaseModel para crear los schemas (estructuras de datos)
# y field_validator para validar automáticamente los campos
from pydantic import BaseModel, ConfigDict, field_validator

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

    # Clave foránea que conecta con la tabla zonas (estaciones meteorológicas)
    # # ID de la zona a la que pertenece la medición (lo envía el usuario) 
    zona_id: int

    # Fecha y hora del dato climático
    fecha_datos: str

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

    """
    Schema usado para crear una nueva medición.

    Mantiene las validaciones personalizadas del proyecto.
    """


    # ------------------------------------------------------
    # VALIDACIÓN DEL ID DE ZONA
    # ------------------------------------------------------
    @field_validator("zona_id")
    @classmethod
    def check_zona_id(cls, value):
        # Comprobamos que el ID sea positivo
        if value <= 0:
            raise ValueError("El ID de zona debe ser mayor que 0")
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
class MeasurementResponse(MeasurementBase):

    """
    Schema usado para devolver una medición desde la API.

    Incluye campos que vienen de la base de datos.
    """
 
    # ID único de la medición (clave primaria) en la base de datos
    id: int 

    # Fecha en la que se guardó el registro en la base de datos (se genera automáticamente)
    created_at: datetime | None = None


    # Permite convertir objetos de SQLAlchemy a JSON automáticamente
    model_config = ConfigDict(from_attributes=True)