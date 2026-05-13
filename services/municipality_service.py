# services/municipality_service.py

"""
Servicio de municipios AEMET.

Este archivo se encarga de resolver qué municipio corresponde a unas coordenadas.

¿Por qué necesitamos esto?
--------------------------
AEMET no devuelve la predicción municipal usando latitud y longitud directamente.

Para pedir la predicción por municipio, AEMET necesita un identificador de municipio,
por ejemplo algo parecido a:

    id28079

Ese identificador representa un municipio concreto.

Flujo que queremos conseguir:
-----------------------------
1. El usuario envía latitud y longitud.
2. Buscamos la estación AEMET más cercana.
3. Usamos las coordenadas de esa estación o del usuario.
4. Buscamos el municipio AEMET más cercano.
5. Obtenemos su código.
6. Pedimos la predicción diaria u horaria de ese municipio.

Este archivo NO llama a la predicción.
Solo resuelve municipios.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from services.aemet_client import AemetClient
from utils.helpers import calcular_distancia


class MunicipalityService:
    """
    Servicio para trabajar con municipios de AEMET.

    Usa AemetClient para obtener el catálogo de municipios y después calcula
    cuál es el municipio más cercano a unas coordenadas.
    """

    def __init__(self, aemet_client: Optional[AemetClient] = None):
        """
        Inicializa el servicio.

        Parámetros:
        -----------
        aemet_client:
            Cliente de AEMET.

        Lo hacemos opcional para facilitar pruebas en el futuro.
        """

        self.logger = logging.getLogger(__name__)
        self.aemet_client = aemet_client or AemetClient()

        # Caché simple en memoria.
        # Así no pedimos el catálogo de municipios a AEMET en cada consulta.
        self._municipios_cache: Optional[List[Dict[str, Any]]] = None

    def obtener_municipio_mas_cercano(
        self,
        lat: Any,
        lon: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Busca el municipio AEMET más cercano a unas coordenadas.

        Parámetros:
        -----------
        lat:
            Latitud.

        lon:
            Longitud.

        Devuelve:
        ---------
        Un diccionario normalizado con información del municipio:

        {
            "codigo": "id28079",
            "nombre": "Madrid",
            "provincia": "Madrid",
            "lat": 40.4167,
            "lon": -3.7033,
            "distancia_km": 1.25,
            "raw": {...}
        }

        Si no se puede resolver, devuelve None.
        """

        try:
            lat_usuario = self._to_float(lat)
            lon_usuario = self._to_float(lon)

        except ValueError:
            self.logger.error(
                "Coordenadas inválidas para resolver municipio: lat=%s lon=%s",
                lat,
                lon,
            )
            return None

        municipios = self._obtener_municipios()

        if not municipios:
            self.logger.warning("No hay municipios disponibles desde AEMET.")
            return None

        municipio_cercano = None
        distancia_minima = float("inf")

        for municipio in municipios:
            coords = self._extraer_coordenadas_municipio(municipio)

            if coords is None:
                continue

            lat_municipio, lon_municipio = coords

            distancia = calcular_distancia(
                lat_usuario,
                lon_usuario,
                lat_municipio,
                lon_municipio,
            )

            if distancia < distancia_minima:
                distancia_minima = distancia
                municipio_cercano = municipio

        if municipio_cercano is None:
            self.logger.warning(
                "No se pudo encontrar municipio cercano para lat=%s lon=%s",
                lat_usuario,
                lon_usuario,
            )
            return None

        return self._normalizar_municipio(
            municipio=municipio_cercano,
            distancia_km=distancia_minima,
        )

    def obtener_municipio_para_estacion(
        self,
        estacion: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene el municipio más cercano a una estación AEMET.

        Parámetro:
        ----------
        estacion:
            Diccionario con datos de una estación u observación AEMET.

        La estación suele traer:
            {
                "lat": "...",
                "lon": "...",
                "ubi": "...",
                ...
            }

        Devuelve:
        ---------
        Municipio normalizado o None.
        """

        if not estacion:
            return None

        lat = estacion.get("lat")
        lon = estacion.get("lon")

        if lat is None or lon is None:
            self.logger.warning(
                "La estación no tiene coordenadas. No se puede resolver municipio."
            )
            return None

        return self.obtener_municipio_mas_cercano(lat, lon)

    def _obtener_municipios(self) -> List[Dict[str, Any]]:
        """
        Obtiene el catálogo de municipios.

        Primero revisa si ya lo tenemos en caché.
        Si no lo tenemos, lo pide a AEMET usando AemetClient.
        """

        if self._municipios_cache is not None:
            return self._municipios_cache

        municipios = self.aemet_client.obtener_municipios()

        if not isinstance(municipios, list):
            municipios = []

        self._municipios_cache = municipios

        return municipios

    def _normalizar_municipio(
        self,
        municipio: Dict[str, Any],
        distancia_km: float,
    ) -> Dict[str, Any]:
        """
        Convierte un municipio crudo de AEMET a una estructura limpia.

        Como la estructura exacta puede variar, intentamos leer varios nombres
        posibles de campo.
        """

        coords = self._extraer_coordenadas_municipio(municipio)

        if coords:
            lat, lon = coords
        else:
            lat, lon = None, None

        codigo = self._extraer_codigo_municipio(municipio)

        return {
            "codigo": codigo,
            "nombre": self._extraer_nombre_municipio(municipio),
            "provincia": self._extraer_provincia_municipio(municipio),
            "lat": lat,
            "lon": lon,
            "distancia_km": round(distancia_km, 2),
            "raw": municipio,
        }

    def _extraer_codigo_municipio(
        self,
        municipio: Dict[str, Any],
    ) -> Optional[str]:
        """
        Extrae el código de municipio que necesita AEMET.

        AEMET suele usar identificadores del estilo:
            id28079

        Pero dependiendo del origen de datos puede aparecer como:
            "id"
            "codigo"
            "codmun"
            "municipio"
            "ine"

        Este método intenta ser flexible.
        """

        posibles_claves = [
            "id",
            "codigo",
            "codmun",
            "cod_municipio",
            "codigo_municipio",
            "municipio",
            "ine",
        ]

        for clave in posibles_claves:
            valor = municipio.get(clave)

            if valor:
                return self._normalizar_codigo_aemet(valor)

        return None

    def _normalizar_codigo_aemet(self, valor: Any) -> str:
        """
        Normaliza el código de municipio al formato esperado por AEMET.

        Si ya viene como:
            id28079

        lo dejamos igual.

        Si viene como:
            28079

        lo convertimos a:
            id28079
        """

        codigo = str(valor).strip()

        if codigo.startswith("id"):
            return codigo

        # Si viene con espacios o caracteres raros, nos quedamos con dígitos.
        solo_digitos = re.sub(r"\D", "", codigo)

        if solo_digitos:
            return f"id{solo_digitos}"

        return codigo

    def _extraer_nombre_municipio(
        self,
        municipio: Dict[str, Any],
    ) -> Optional[str]:
        """
        Extrae el nombre del municipio.

        Probamos diferentes nombres de campo por seguridad.
        """

        posibles_claves = [
            "nombre",
            "nombre_municipio",
            "municipio",
            "capital",
            "descripcion",
        ]

        for clave in posibles_claves:
            valor = municipio.get(clave)

            if valor:
                return str(valor).strip()

        return None

    def _extraer_provincia_municipio(
        self,
        municipio: Dict[str, Any],
    ) -> Optional[str]:
        """
        Extrae la provincia del municipio si AEMET la proporciona.
        """

        posibles_claves = [
            "provincia",
            "nombre_provincia",
            "prov",
        ]

        for clave in posibles_claves:
            valor = municipio.get(clave)

            if valor:
                return str(valor).strip()

        return None

    def _extraer_coordenadas_municipio(
        self,
        municipio: Dict[str, Any],
    ) -> Optional[Tuple[float, float]]:
        """
        Extrae latitud y longitud del municipio.

        AEMET puede devolver coordenadas con distintos nombres:

        - latitud_dec
        - longitud_dec
        - latitud
        - longitud
        - lat
        - lon

        Este método intenta cubrir esos casos.
        """

        posibles_latitudes = [
            municipio.get("latitud_dec"),
            municipio.get("latitud"),
            municipio.get("lat"),
            municipio.get("latitude"),
        ]

        posibles_longitudes = [
            municipio.get("longitud_dec"),
            municipio.get("longitud"),
            municipio.get("lon"),
            municipio.get("lng"),
            municipio.get("longitude"),
        ]

        lat = self._primer_float_valido(posibles_latitudes)
        lon = self._primer_float_valido(posibles_longitudes)

        if lat is None or lon is None:
            return None

        return lat, lon

    def _primer_float_valido(
        self,
        valores: List[Any],
    ) -> Optional[float]:
        """
        Devuelve el primer valor que se pueda convertir a float.

        Si ninguno sirve, devuelve None.
        """

        for valor in valores:
            try:
                return self._to_float(valor)

            except ValueError:
                continue

        return None

    @staticmethod
    def _to_float(valor: Any) -> float:
        """
        Convierte un valor a float.

        Soporta:
        - números normales,
        - strings con punto decimal,
        - strings con coma decimal.

        Ejemplos:
            "40.4168" -> 40.4168
            "40,4168" -> 40.4168
            40.4168   -> 40.4168
        """

        if valor is None:
            raise ValueError("Valor vacío")

        if isinstance(valor, str):
            valor = valor.strip().replace(",", ".")

            if valor == "":
                raise ValueError("Valor vacío")

        try:
            return float(valor)

        except (TypeError, ValueError):
            raise ValueError(f"No se puede convertir a float: {valor}")