# services/weather_api_service.py

"""
Servicio principal de clima.

Este archivo contiene la lógica de negocio relacionada con el clima.

Responsabilidad de este archivo:
--------------------------------
1. Recibir unas coordenadas del usuario: latitud y longitud.
2. Pedir a AEMET las observaciones actuales.
3. Buscar la estación meteorológica más cercana.
4. Resolver el municipio más cercano.
5. Pedir predicción diaria y horaria para ese municipio.
6. Devolver un único diccionario con:
   - observación real de la estación más cercana,
   - municipio detectado,
   - predicción diaria,
   - predicción horaria.

Importante:
-----------
Este archivo NO hace las peticiones HTTP directamente a AEMET.
Eso lo hace:

    services/aemet_client.py

Este archivo NO convierte los datos al formato final del frontend.
Eso lo hace:

    services/normalizer_service.py
"""

import logging
from typing import Any, Dict, List, Optional

from services.retry_service import get_retry_session
from services.aemet_client import AemetClient
from services.municipality_service import MunicipalityService
from utils.helpers import calcular_distancia


class WeatherAPIService:
    """
    Servicio de alto nivel para obtener datos meteorológicos.

    Este servicio junta varias piezas:

    - AemetClient:
        Hace las peticiones reales a AEMET.

    - MunicipalityService:
        Resuelve el municipio más cercano y su código AEMET.

    - calcular_distancia:
        Calcula qué estación está más cerca del usuario.
    """

    def __init__(
        self,
        aemet_client: Optional[AemetClient] = None,
        municipality_service: Optional[MunicipalityService] = None,
    ):
        """
        Inicializa el servicio.

        Parámetros:
        -----------
        aemet_client:
            Cliente de AEMET. Si no se pasa, creamos uno real.

        municipality_service:
            Servicio de municipios. Si no se pasa, creamos uno real.

        Lo dejamos así para que en tests futuros podamos inyectar versiones falsas.
        """

        self.logger = logging.getLogger(__name__)

        self.aemet_client = aemet_client or AemetClient()
        if aemet_client is None:
            self.aemet_client.session = get_retry_session()
        self.municipality_service = (
            municipality_service
            or MunicipalityService(aemet_client=self.aemet_client)
        )

    def obtener_clima_por_coordenadas(
        self,
        user_lat: Any,
        user_lon: Any,
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene clima completo para unas coordenadas.

        Flujo:
        ------
        1. Convertimos lat/lon a float.
        2. Pedimos observaciones actuales a AEMET.
        3. Buscamos la estación más cercana.
        4. Resolvemos el municipio más cercano a esa estación.
        5. Pedimos predicción diaria y horaria del municipio.
        6. Devolvemos un único diccionario enriquecido.

        Devuelve:
        ---------
        Un diccionario con datos crudos + campos añadidos por nuestra app.
        """

        try:
            lat = self._convertir_a_float(user_lat)
            lon = self._convertir_a_float(user_lon)

        except ValueError:
            self.logger.error(
                "Coordenadas inválidas recibidas: lat=%s lon=%s",
                user_lat,
                user_lon,
            )
            return None

        # 1. Pedimos observaciones actuales a AEMET.
        observaciones = self.aemet_client.obtener_observaciones_actuales()

        if not observaciones:
            self.logger.warning("No se recibieron observaciones actuales de AEMET.")
            return None

        # 2. Buscamos la estación AEMET más cercana al usuario.
        estacion_cercana = self._buscar_estacion_mas_cercana(
            user_lat=lat,
            user_lon=lon,
            observaciones=observaciones,
        )

        if not estacion_cercana:
            self.logger.warning(
                "No se pudo calcular estación cercana para lat=%s lon=%s",
                lat,
                lon,
            )
            return None

        # 3. Resolvemos municipio más cercano.
        #
        # Usamos la estación cercana porque es el punto de medición real.
        # Si la estación no permite resolver municipio, probamos con las coordenadas
        # originales del usuario como plan B.
        municipio = self.municipality_service.obtener_municipio_para_estacion(
            estacion_cercana
        )

        if not municipio:
            municipio = self.municipality_service.obtener_municipio_mas_cercano(
                lat,
                lon,
            )

        # 4. Pedimos predicciones si hemos podido obtener código de municipio.
        prediccion_diaria = None
        prediccion_horaria = None

        codigo_municipio = None

        if municipio:
            codigo_municipio = municipio.get("codigo")

        if codigo_municipio:
            prediccion_diaria = self.aemet_client.obtener_prediccion_municipio_diaria(
                codigo_municipio
            )

            prediccion_horaria = self.aemet_client.obtener_prediccion_municipio_horaria(
                codigo_municipio
            )

        # 5. Enriquecemos la estación cercana con información útil.
        #
        # Importante:
        # No eliminamos los campos originales de AEMET:
        #   ta, hr, vv, prec, pres, ubi, fint...
        #
        # Los mantenemos porque normalizer_service.py los necesita.
        estacion_cercana["municipio_detectado"] = municipio
        estacion_cercana["codigo_municipio"] = codigo_municipio
        estacion_cercana["prediccion_diaria"] = prediccion_diaria
        estacion_cercana["prediccion_horaria"] = prediccion_horaria

        self.logger.info(
            "Clima completo obtenido. Estación=%s Municipio=%s Distancia=%.2f km",
            estacion_cercana.get("ubi", "desconocida"),
            municipio.get("nombre") if municipio else "no resuelto",
            estacion_cercana.get("distancia_estacion_km", -1),
        )

        return estacion_cercana

    def _buscar_estacion_mas_cercana(
        self,
        user_lat: float,
        user_lon: float,
        observaciones: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Busca la estación meteorológica más cercana al usuario.

        Cada observación de AEMET suele traer:
            - lat
            - lon
            - ubi
            - idema
            - ta
            - hr
            - vv
            - prec
            - pres

        Recorremos todas las observaciones y calculamos la distancia con
        la función calcular_distancia() de utils/helpers.py.
        """

        estacion_cercana = None
        distancia_minima = float("inf")

        for observacion in observaciones:
            try:
                estacion_lat = self._convertir_a_float(observacion.get("lat"))
                estacion_lon = self._convertir_a_float(observacion.get("lon"))

                distancia = calcular_distancia(
                    user_lat,
                    user_lon,
                    estacion_lat,
                    estacion_lon,
                )

                if distancia < distancia_minima:
                    distancia_minima = distancia

                    # Copiamos la observación para no modificar el objeto original
                    # que viene de la lista de AEMET.
                    estacion_cercana = observacion.copy()

            except (ValueError, TypeError):
                # Algunas estaciones pueden venir sin coordenadas.
                # Las ignoramos para no romper toda la consulta.
                continue

        if not estacion_cercana:
            return None

        # Campos añadidos por nuestra app.
        estacion_cercana["distancia_estacion_km"] = round(distancia_minima, 2)
        estacion_cercana["lat_usuario"] = user_lat
        estacion_cercana["lon_usuario"] = user_lon

        return estacion_cercana

    def obtener_clima_por_id(self, station_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos meteorológicos de una estación concreta.

        Este método lo dejamos preparado por si más adelante queremos
        consultar una estación AEMET concreta por su ID.
        """

        observaciones = self.aemet_client.obtener_observacion_por_estacion(station_id)

        if not observaciones:
            return None

        ultima_observacion = observaciones[-1]
        return ultima_observacion

    @staticmethod
    def _convertir_a_float(valor: Any) -> float:
        """
        Convierte un valor a float de forma segura.

        Soporta:
        - "40.4168"
        - "40,4168"
        - 40.4168

        Si no puede convertirlo, lanza ValueError.
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


# -------------------------------------------------------------------------
# FUNCIÓN PUENTE PARA COMPATIBILIDAD CON EL CONTROLADOR ACTUAL
# -------------------------------------------------------------------------
#
# controllers/api_controller.py importa esta función directamente:
#
#     from services.weather_api_service import obtener_clima_por_coordenadas
#
# Por eso mantenemos esta función fuera de la clase.
# Así no necesitamos tocar todavía controllers/api_controller.py.
# -------------------------------------------------------------------------

def obtener_clima_por_coordenadas(lat: Any, lon: Any) -> Optional[Dict[str, Any]]:
    """
    Función puente usada por controllers/api_controller.py.

    Recibe latitud y longitud, crea el servicio principal y devuelve
    los datos enriquecidos de AEMET.
    """

    service = WeatherAPIService()
    return service.obtener_clima_por_coordenadas(lat, lon)
