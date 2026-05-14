# Para manejar fechas reales (created_at) que vienen de la base de datos
from datetime import datetime  

# Importamos la función centralizada para validar fechas (evita duplicar lógica)
from utils.datetime_utils import validar_fecha

# Importamos BaseModel para crear los schemas (estructuras de datos)
# y field_validator para validar automáticamente los campos
from pydantic import BaseModel, ConfigDict, field_validator

# Importamos Optional para poder definir campos opcionales (None),
# necesario en actualizaciones parciales (PATCH)
from typing import Optional

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
class MedicionBase(BaseModel):

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
class MedicionCrear(MedicionBase):

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


    # ---------------------------------------------------------
    # VALIDACIÓN DE FECHA DE LOS DATOS
    # ---------------------------------------------------------
    @field_validator("fecha_datos")
    @classmethod
    def check_fecha_datos(cls, value):
        """
        Valida que fecha_datos tenga un formato correcto antes de crear
        una nueva medición.
        """

        if not validar_fecha(value):
            raise ValueError("La fecha debe tener un formato válido")

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


# ============================================================
# SCHEMA DE ACTUALIZACIÓN (UPDATE / PATCH)
# ============================================================
# Se usa para actualizar una medición existente.
# Todos los campos son opcionales porque en un PATCH
# se puede actualizar solo un dato, por ejemplo solo temperatura.

class MedicionActualizar(BaseModel):

    zona_id: Optional[int] = None
    fecha_datos: Optional[str] = None
    temperatura: Optional[float] = None
    humedad: Optional[float] = None
    viento: Optional[float] = None
    lluvia: Optional[float] = None

    @field_validator("zona_id")
    @classmethod
    def check_zona_id(cls, value):
        if value is None:
            return value

        if value <= 0:
            raise ValueError("El ID de zona debe ser mayor que 0")

        return value

    @field_validator("fecha_datos")
    @classmethod
    def check_fecha_datos(cls, value):
        if value is None:
            return value

        if not validar_fecha(value):
            raise ValueError("La fecha debe tener un formato válido")

        return value

    @field_validator("temperatura")
    @classmethod
    def check_temperatura(cls, value):
        if value is None:
            return value

        if not validar_temperatura(value):
            raise ValueError("La temperatura debe estar entre -50 y 60 grados")

        return value

    @field_validator("humedad")
    @classmethod
    def check_humedad(cls, value):
        if value is None:
            return value

        if not validar_humedad(value):
            raise ValueError("La humedad debe estar entre 0 y 100")

        return value

    @field_validator("viento")
    @classmethod
    def check_viento(cls, value):
        if value is None:
            return value

        if not validar_viento(value):
            raise ValueError("El viento debe ser mayor o igual que 0")

        return value

    @field_validator("lluvia")
    @classmethod
    def check_lluvia(cls, value):
        if value is None:
            return value

        if not validar_lluvia(value):
            raise ValueError("La lluvia debe ser mayor o igual que 0")

        return value


# ==========================================================
# SCHEMA DE SALIDA (RESPONSE)
# ==========================================================
class MedicionRespuesta(MedicionBase):

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