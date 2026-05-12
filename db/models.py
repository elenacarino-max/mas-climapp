from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
# Column    → define una columna de la tabla
# Integer   → número entero (para ids y claves foráneas)
# String    → texto con longitud máxima
# Float     → número decimal (temperaturas, humedad...)
# DateTime  → fecha y hora (para created_at)
# ForeignKey → enlaza una columna con la clave primaria de otra tabla

from sqlalchemy.orm import relationship
# relationship → define la relación entre dos modelos en Python
# (no crea columnas extra, es solo para que SQLAlchemy sepa navegar entre objetos)

from datetime import datetime, timezone
# datetime  → para generar la fecha y hora actuales
# timezone  → para que la hora se guarde siempre en UTC, independiente del servidor

from db.database import Base
# Base es la clase madre definida en database.py.
# Todo modelo que herede de Base se convierte en una tabla de la BD.


class Zona(Base):
    """
    Tabla 'zonas': representa un municipio y su estación meteorológica.

    Evolución desde el Proyecto 2:
        En el P2, Zona era una clase Python simple (models/zona.py) que
        se guardaba en un archivo JSON. Ahora es una tabla SQL real con
        clave primaria propia, lo que permite relacionarla con Medicion.

    Campos heredados del P2 (models/zona.py):
        municipio, cod_ine, id_estacion, estacion_referencia
    """

    # Le dice a SQLAlchemy cómo se llama la tabla en la base de datos.
    # Si no se pone, SQLAlchemy usaría el nombre de la clase en minúsculas.
    __tablename__ = "zonas"

    # Clave primaria: número entero que se asigna solo (1, 2, 3...).
    # primary_key=True → es la columna identificadora única de cada fila.
    # index=True       → crea un índice para que las búsquedas por id sean rápidas.
    # autoincrement    → la BD asigna el número sola, no hay que pasarlo al crear una zona.
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Nombre del municipio. nullable=False significa que es obligatorio,
    # la BD rechazará cualquier insert que no incluya este campo.
    municipio = Column(String(100), nullable=False)

    # Código INE del municipio (identificador oficial del INE, ej: "28079" para Madrid).
    # unique=True  → no puede haber dos zonas con el mismo cod_ine.
    # nullable=False → obligatorio.
    # index=True   → búsquedas por cod_ine serán rápidas (lo usará el ETL para evitar duplicados).
    cod_ine = Column(String(20), unique=True, nullable=False, index=True)

    # Identificador de la estación AEMET asociada a este municipio (ej: "3195").
    id_estacion = Column(String(50), nullable=False)

    # Nombre descriptivo de la estación (ej: "Madrid Retiro").
    estacion_referencia = Column(String(150), nullable=False)

    # Relación con Medicion: le dice a SQLAlchemy que una Zona puede tener muchas Mediciones.
    # back_populates="zona"         → el lado inverso está en Medicion.zona
    # cascade="all, delete-orphan"  → si borramos una Zona, se borran también TODAS sus
    #                                  mediciones automáticamente. Esto cumple el requisito
    #                                  de integridad referencial del checklist del P3
    #                                  (no puede haber mediciones sin zona).
    mediciones = relationship("Medicion", back_populates="zona", cascade="all, delete-orphan")

    def __repr__(self):
        # Representación legible al hacer print() de un objeto Zona en la consola.
        # Útil para depurar: print(zona) → <Zona id=1 municipio=Madrid estacion=3195>
        return f"<Zona id={self.id} municipio={self.municipio} estacion={self.id_estacion}>"


class Medicion(Base):
    """
    Tabla 'mediciones': representa un registro climático de una zona en una fecha concreta.

    Evolución desde el Proyecto 2:
        En el P2, los datos climáticos se guardaban en registros_climaticos.json
        y en la tabla registros_clima de clima.db (todo mezclado en una sola tabla).
        Ahora separamos zona y medición en dos tablas distintas relacionadas por FK,
        lo que es la forma correcta de modelar esta relación en SQL.

    Campos heredados del P2 (models/registro_climatico.py y tabla registros_clima):
        temperatura, humedad, viento, lluvia, presion
    Campos nuevos en el P3:
        zona_id  → la FK que vincula cada medición a su zona
        created_at → timestamp de cuándo se insertó el dato (trazabilidad del ETL)
    """

    __tablename__ = "mediciones"

    # Clave primaria autoincremental, igual que en Zona.
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Clave foránea: número entero que apunta al 'id' de la tabla 'zonas'.
    # ForeignKey("zonas.id") → la BD garantiza que zona_id siempre existe en zonas.id.
    #                          Si intentas insertar una medición con un zona_id que no existe
    #                          en la tabla zonas, la BD lo rechazará con un error.
    # nullable=False → toda medición DEBE pertenecer a una zona. No hay mediciones huérfanas.
    # index=True     → acelera consultas del tipo "dame todas las mediciones de la zona 5".
    zona_id = Column(Integer, ForeignKey("zonas.id"), nullable=False, index=True)

    # Fecha a la que corresponden los datos climáticos (ej: "2024-06-15").
    # Es String y no Date para mantener compatibilidad con el formato que venía del P2.
    # nullable=False → toda medición debe tener fecha.
    fecha_datos = Column(String(50), nullable=False)

    # Datos climáticos heredados del P2. Son nullable=True porque a veces
    # la AEMET no devuelve todos los valores (sensores sin datos, mantenimiento...).
    # El ETL (Persona 3) se encargará de gestionar estos nulos con Pandas.
    temperatura = Column(Float, nullable=True)  # en grados Celsius
    humedad     = Column(Float, nullable=True)  # en porcentaje (0-100)
    viento      = Column(Float, nullable=True)  # en km/h
    lluvia      = Column(Float, nullable=True)  # en mm
    
    # Timestamp UTC de cuándo se insertó este registro en la BD.
    # Lo usa el ETL para el log de trazabilidad (requisito del checklist del P3).
    # default=lambda: datetime.now(timezone.utc) → se calcula automáticamente al insertar,
    #   no hace falta pasarlo manualmente.
    # timezone.utc → guardamos siempre en hora universal para evitar problemas con
    #   cambios de horario (verano/invierno) o servidores en distintas zonas horarias.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relación inversa hacia Zona: permite hacer medicion.zona para obtener el objeto Zona
    # completo sin hacer una query manual. Solo existe en Python, no añade columnas a la BD.
    # back_populates="mediciones" → enlaza con el atributo 'mediciones' de la clase Zona.
    zona = relationship("Zona", back_populates="mediciones")

    def __repr__(self):
        # Representación legible al hacer print() de un objeto Medicion.
        # Ejemplo: <Medicion id=42 zona_id=1 fecha=2024-06-15 temp=28.3>
        return (
            f"<Medicion id={self.id} zona_id={self.zona_id} "
            f"fecha={self.fecha_datos} temp={self.temperatura}>"
        )