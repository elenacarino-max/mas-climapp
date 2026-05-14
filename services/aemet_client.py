# services/aemet_client.py

"""
Cliente de AEMET OpenData.

Este archivo contiene únicamente la lógica de comunicación con la API externa
de AEMET.
"""

import logging
import os
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv

from services.retry_service import get_retry_session


load_dotenv()


class AemetClient:
    """
    Cliente reutilizable para comunicarnos con AEMET OpenData.
    """

    def __init__(self):
        self.api_key = os.getenv("AEMET_API_KEY")

        if not self.api_key:
            raise ValueError(
                "AEMET_API_KEY no encontrada. "
                "Añádela en el archivo .env de la raíz del proyecto."
            )

        self.session = get_retry_session()
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://opendata.aemet.es/opendata"

    def _headers(self) -> Dict[str, str]:
        """
        Cabeceras necesarias para llamar a AEMET.
        """

        return {
            "api_key": self.api_key,
            "cache-control": "no-cache",
        }

    def _get_payload_from_endpoint(self, endpoint: str) -> Optional[Any]:
        """
        Ejecuta la doble petición típica de AEMET.

        1. Llama al endpoint de AEMET.
        2. AEMET devuelve un JSON con una URL en el campo "datos".
        3. Se hace una segunda petición a esa URL.
        4. Se devuelve el JSON real.
        """

        url = f"{self.base_url}{endpoint}"

        try:
            # Primera petición: metadatos.
            response_metadata = self.session.get(
                url,
                headers=self._headers(),
                timeout=20,
            )
            response_metadata.raise_for_status()

            metadata = response_metadata.json()
            data_url = metadata.get("datos")

            if not data_url:
                self.logger.warning(
                    "AEMET no devolvió URL de datos. endpoint=%s respuesta=%s",
                    endpoint,
                    metadata,
                )
                return None

            # Segunda petición: datos reales.
            response_payload = self.session.get(
                data_url,
                timeout=20,
            )
            response_payload.raise_for_status()

            return response_payload.json()

        except requests.exceptions.Timeout as error:
            self.logger.error(
                "Timeout llamando a AEMET. endpoint=%s error=%s",
                endpoint,
                error,
            )
            return None

        except requests.exceptions.ConnectionError as error:
            self.logger.error(
                "Error de conexión con AEMET. endpoint=%s error=%s",
                endpoint,
                error,
            )
            return None

        except requests.exceptions.HTTPError as error:
            self.logger.error(
                "Error HTTP de AEMET. endpoint=%s status_code=%s error=%s",
                endpoint,
                getattr(error.response, "status_code", None),
                error,
            )
            return None

        except ValueError as error:
            self.logger.error(
                "Respuesta JSON inválida de AEMET. endpoint=%s error=%s",
                endpoint,
                error,
            )
            return None

    def _normalizar_codigo_municipio_para_prediccion(
        self,
        codigo_municipio: str,
    ) -> str:
        """
        Normaliza el código de municipio para endpoints de predicción.

        Ejemplo:
        - id28079 -> 28079
        - 28079   -> 28079
        """

        codigo = str(codigo_municipio).strip()

        if codigo.startswith("id"):
            return codigo[2:]

        return codigo

    def obtener_observaciones_actuales(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las observaciones actuales de estaciones AEMET.
        """

        endpoint = "/api/observacion/convencional/todas"
        payload = self._get_payload_from_endpoint(endpoint)

        if isinstance(payload, list):
            return payload

        return []

    def obtener_observacion_por_estacion(
        self,
        idema: str,
    ) -> List[Dict[str, Any]]:
        """
        Obtiene observaciones actuales de una estación concreta.
        """

        endpoint = f"/api/observacion/convencional/datos/estacion/{idema}"
        payload = self._get_payload_from_endpoint(endpoint)

        if isinstance(payload, list):
            return payload

        return []

    def obtener_prediccion_municipio_diaria(
        self,
        codigo_municipio: str,
    ) -> Optional[Any]:
        """
        Obtiene la predicción diaria de un municipio.
        """

        codigo_prediccion = self._normalizar_codigo_municipio_para_prediccion(
            codigo_municipio
        )

        endpoint = (
            f"/api/prediccion/especifica/municipio/diaria/{codigo_prediccion}"
        )

        payload = self._get_payload_from_endpoint(endpoint)

        if isinstance(payload, dict):
            return payload

        if isinstance(payload, list):
            return payload

        return None

    def obtener_prediccion_municipio_horaria(
        self,
        codigo_municipio: str,
    ) -> Optional[Any]:
        """
        Obtiene la predicción horaria de un municipio.
        """

        codigo_prediccion = self._normalizar_codigo_municipio_para_prediccion(
            codigo_municipio
        )

        endpoint = (
            f"/api/prediccion/especifica/municipio/horaria/{codigo_prediccion}"
        )

        payload = self._get_payload_from_endpoint(endpoint)

        if isinstance(payload, dict):
            return payload

        if isinstance(payload, list):
            return payload

        return None

    def obtener_municipios(self) -> List[Dict[str, Any]]:
        """
        Obtiene el catálogo de municipios desde AEMET.
        """

        endpoint = "/api/maestro/municipios"
        payload = self._get_payload_from_endpoint(endpoint)

        if isinstance(payload, list):
            return payload

        return []