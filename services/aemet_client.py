# services/aemet_client.py

"""
Cliente de AEMET OpenData.

Este archivo contiene únicamente la lógica de comunicación con la API externa
de AEMET.

Responsabilidades:
------------------
1. Leer la API Key de AEMET desde variables de entorno.
2. Llamar a endpoints de AEMET.
3. Resolver la doble petición típica de AEMET:
   - primera petición: devuelve una URL en el campo "datos"
   - segunda petición: descarga los datos reales desde esa URL
4. Devolver datos crudos para que otros servicios los procesen.

Este archivo NO:
----------------
- calcula estaciones cercanas,
- normaliza datos para el frontend,
- decide qué se muestra al usuario,
- guarda registros.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from services.retry_service import get_retry_session


# Cargamos el archivo .env también cuando este módulo se usa fuera de app.py.
# Por ejemplo:
# python -c "from services.aemet_client import AemetClient"
load_dotenv()


class AemetClient:
    """
    Cliente reutilizable para comunicarnos con AEMET OpenData.
    """

    def __init__(self):
        """
        Inicializa el cliente.

        La clave debe estar en el archivo .env de la raíz del proyecto:

            AEMET_API_KEY=tu_clave_aqui
        """

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

        AEMET espera la API key en la cabecera HTTP llamada api_key.
        """

        return {
            "api_key": self.api_key,
            "cache-control": "no-cache",
        }

    def _get_payload_from_endpoint(self, endpoint: str) -> Optional[Any]:
        """
        Ejecuta la doble petición típica de AEMET.

        Flujo:
        ------
        1. Llamamos al endpoint real de AEMET.
        2. AEMET devuelve un JSON de metadatos con una URL en "datos".
        3. Hacemos una segunda petición a esa URL.
        4. Devolvemos el JSON real.

        Ejemplo de primera respuesta de AEMET:
        --------------------------------------
        {
            "descripcion": "...",
            "estado": 200,
            "datos": "https://opendata.aemet.es/opendata/sh/..."
        }
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

        except Exception as error:
            self.logger.error(
                "Error llamando a AEMET. endpoint=%s error=%s",
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

        El catálogo de municipios puede devolver códigos como:

            id28079

        Pero los endpoints de predicción municipal suelen esperar:

            28079

        Por eso quitamos el prefijo "id" si viene incluido.
        """

        codigo = str(codigo_municipio).strip()

        if codigo.startswith("id"):
            return codigo[2:]

        return codigo

    def obtener_observaciones_actuales(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las observaciones actuales de estaciones AEMET.

        Endpoint:
            /api/observacion/convencional/todas

        Devuelve:
            Lista de observaciones crudas de AEMET.
        """

        endpoint = "/api/observacion/convencional/todas"
        payload = self._get_payload_from_endpoint(endpoint)

        if isinstance(payload, list):
            return payload

        return []

    def obtener_observacion_por_estacion(self, idema: str) -> List[Dict[str, Any]]:
        """
        Obtiene observaciones actuales de una estación concreta.

        Parámetro:
        ----------
        idema:
            Identificador de estación AEMET.

        Endpoint:
            /api/observacion/convencional/datos/estacion/{idema}
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

        Parámetro:
        ----------
        codigo_municipio:
            Código de municipio. Puede venir como "id28079" o "28079".

        Endpoint:
            /api/prediccion/especifica/municipio/diaria/{municipio}

        AEMET puede devolver dict o list, por eso aceptamos ambos.
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

        Parámetro:
        ----------
        codigo_municipio:
            Código de municipio. Puede venir como "id28079" o "28079".

        Endpoint:
            /api/prediccion/especifica/municipio/horaria/{municipio}

        AEMET puede devolver dict o list, por eso aceptamos ambos.
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

        Endpoint:
            /api/maestro/municipios

        Lo usamos para resolver:
            coordenadas -> municipio -> código AEMET
        """

        endpoint = "/api/maestro/municipios"
        payload = self._get_payload_from_endpoint(endpoint)

        if isinstance(payload, list):
            return payload

        return []