# services/municipality_service.py

import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from services.aemet_client import AemetClient
from utils.helpers import calcular_distancia


class MunicipalityService:
    """
    Servicio para trabajar con municipios de AEMET.
    """

    def __init__(self, aemet_client: Optional[AemetClient] = None):
        self.logger = logging.getLogger(__name__)
        self.aemet_client = aemet_client or AemetClient()

        # Caché simple en memoria.
        # Solo se rellenará si AEMET devuelve una lista válida y con datos.
        self._municipios_cache: Optional[List[Dict[str, Any]]] = None

    def obtener_municipio_mas_cercano(
        self,
        lat: Any,
        lon: Any,
    ) -> Optional[Dict[str, Any]]:

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

        Importante:
        - Si ya hay caché válida, la devuelve.
        - Si AEMET falla o devuelve algo inválido, NO guarda [] en caché.
        - Así evitamos que un fallo temporal deje el servicio bloqueado
          con una lista vacía hasta reiniciar la app.
        """

        if self._municipios_cache is not None:
            return self._municipios_cache

        municipios = self.aemet_client.obtener_municipios()

        if not isinstance(municipios, list):
            self.logger.warning(
                "No se guarda caché de municipios: respuesta inválida de AEMET. "
                "Tipo recibido: %s",
                type(municipios).__name__,
            )
            return []

        if not municipios:
            self.logger.warning(
                "No se guarda caché de municipios: AEMET devolvió una lista vacía."
            )
            return []

        self._municipios_cache = municipios

        return municipios

    def _normalizar_municipio(
        self,
        municipio: Dict[str, Any],
        distancia_km: float,
    ) -> Dict[str, Any]:

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
        codigo = str(valor).strip()

        if codigo.startswith("id"):
            return codigo

        solo_digitos = re.sub(r"\D", "", codigo)

        if solo_digitos:
            return f"id{solo_digitos}"

        return codigo

    def _extraer_nombre_municipio(
        self,
        municipio: Dict[str, Any],
    ) -> Optional[str]:

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

        for valor in valores:
            try:
                return self._to_float(valor)

            except ValueError:
                continue

        return None

    @staticmethod
    def _to_float(valor: Any) -> float:
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