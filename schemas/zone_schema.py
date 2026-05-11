from pydantic import BaseModel, ConfigDict


# Clase base con los campos comunes de una zona
class ZonaBase(BaseModel):
    """
    Representa una zona geográfica (municipio + estación meteorológica).

    IMPORTANTE:
    Los nombres de los campos se mantienen en español porque
    deben coincidir con la base de datos.
    """

    municipio: str              # Nombre del municipio
    cod_ine: str                # Código INE (identificador único)
    id_estacion: str            # ID de la estación meteorológica
    estacion_referencia: str    # Nombre descriptivo de la estación


# Para crear una nueva zona
class ZonaCrear(ZonaBase):
    """
    Se usa cuando queremos crear una zona (POST).

    No incluimos el id porque lo genera la base de datos automáticamente.
    """
    pass


# Para actualizar una zona
class ZonaActualizar(ZonaBase):
    """
    Se usa para actualizar una zona existente (PUT/PATCH).

    Todos los campos son opcionales porque podemos modificar solo uno.
    """

    municipio: str | None = None
    cod_ine: str | None = None
    id_estacion: str | None = None
    estacion_referencia: str | None = None


# Para devolver datos al cliente
class ZonaRespuesta(ZonaBase):
    """
    Se usa en las respuestas de la API (GET).

    Incluye el id porque la zona ya existe en la base de datos.
    """

    id: int  # Clave primaria

    # Permite convertir objetos de SQLAlchemy a JSON automáticamente
    model_config = ConfigDict(from_attributes=True)