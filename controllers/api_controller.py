# controllers/api_controller.py

"""
Controlador de API.

Este archivo define los endpoints que devuelven datos en formato JSON.

Endpoint principal:
-------------------
GET /api/clima?lat=40.4168&lon=-3.7038

Responsabilidad de este archivo:
--------------------------------
1. Recibir la petición HTTP.
2. Validar que vienen latitud y longitud.
3. Llamar al servicio de clima.
4. Normalizar la respuesta.
5. Guardar el registro en JSON.
6. Devolver la respuesta al frontend.

Importante:
-----------
Este archivo NO debe contener lógica de AEMET.
Este archivo NO debe calcular estaciones cercanas.
Este archivo NO debe normalizar campos técnicos de AEMET.

Eso lo hacen:
- services/weather_api_service.py
- services/aemet_client.py
- services/normalizer_service.py
"""

import logging

from flask import Blueprint, jsonify, request

from repositories.json_repository import guardar_registro
from services.normalizer_service import normalizar_datos_aemet
from services.weather_api_service import obtener_clima_por_coordenadas


api_bp = Blueprint("api", __name__)

logger = logging.getLogger(__name__)


@api_bp.route("/api/clima", methods=["GET"])
def api_clima():
    """
    Devuelve datos climáticos para unas coordenadas.

    Ejemplo de llamada desde el navegador o frontend:

        /api/clima?lat=40.4168&lon=-3.7038

    Parámetros esperados:
    ---------------------
    lat:
        Latitud del usuario.

    lon:
        Longitud del usuario.

    Respuesta:
    ----------
    JSON con:
    - estación AEMET más cercana,
    - temperatura,
    - humedad,
    - viento,
    - lluvia,
    - presión,
    - municipio detectado,
    - predicción diaria,
    - predicción horaria,
    - alertas.
    """

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    # ---------------------------------------------------------
    # 1. Validación básica de parámetros
    # ---------------------------------------------------------
    if not lat or not lon:
        return jsonify(
            {
                "error": "Faltan coordenadas",
                "detalle": "Debes enviar lat y lon. Ejemplo: /api/clima?lat=40.4168&lon=-3.7038",
            }
        ), 400

    # Validamos que lat/lon sean números antes de llamar al servicio.
    try:
        float(str(lat).replace(",", "."))
        float(str(lon).replace(",", "."))

    except ValueError:
        return jsonify(
            {
                "error": "Coordenadas inválidas",
                "detalle": "lat y lon deben ser valores numéricos.",
                "lat_recibida": lat,
                "lon_recibida": lon,
            }
        ), 400

    try:
        # ---------------------------------------------------------
        # 2. Obtener datos crudos enriquecidos desde el servicio
        # ---------------------------------------------------------
        raw_data = obtener_clima_por_coordenadas(lat, lon)

        if not raw_data:
            return jsonify(
                {
                    "error": "No se pudieron obtener datos de AEMET",
                    "detalle": "AEMET no devolvió observaciones válidas para esas coordenadas.",
                    "lat": lat,
                    "lon": lon,
                }
            ), 502

        # ---------------------------------------------------------
        # 3. Normalizar datos para frontend
        # ---------------------------------------------------------
        data = normalizar_datos_aemet(raw_data)

        if not isinstance(data, dict):
            return jsonify(
                {
                    "error": "Error al normalizar datos climáticos",
                    "detalle": "El normalizador no devolvió un diccionario válido.",
                }
            ), 500

        # ---------------------------------------------------------
        # 4. Añadir campos de compatibilidad con el resto de la app
        # ---------------------------------------------------------

        # El repositorio actual filtra registros usando el campo "municipio".
        # Por eso añadimos municipio aunque la respuesta principal tenga
        # "municipio_detectado".
        municipio_detectado = data.get("municipio_detectado") or {}

        if isinstance(municipio_detectado, dict):
            nombre_municipio = municipio_detectado.get("nombre")
        else:
            nombre_municipio = None

        data["municipio"] = (
            nombre_municipio
            or data.get("ciudad")
            or data.get("estacion")
            or "Ubicación detectada"
        )

        # Mantenemos ciudad por compatibilidad con el frontend actual.
        if "ciudad" not in data or not data.get("ciudad"):
            data["ciudad"] = data["municipio"]

        # Añadimos la fuente para que los filtros manual/aemet funcionen.
        data["fuente"] = "aemet"

        # Guardamos también las coordenadas originales recibidas.
        data["consulta"] = {
            "lat": float(str(lat).replace(",", ".")),
            "lon": float(str(lon).replace(",", ".")),
        }

        # ---------------------------------------------------------
        # 5. Guardar registro
        # ---------------------------------------------------------
        #
        # Si el guardado falla, no rompemos la respuesta al usuario.
        # Solo añadimos una advertencia.
        guardado_correcto = guardar_registro(data)

        if not guardado_correcto:
            logger.warning("No se pudo guardar el registro climático en JSON.")
            data["warning"] = "Datos obtenidos, pero no se pudieron guardar."

        # ---------------------------------------------------------
        # 6. Respuesta final
        # ---------------------------------------------------------
        return jsonify(data), 200

    except Exception as error:
        logger.exception("Error en api_controller.api_clima")

        return jsonify(
            {
                "error": "Error interno al consultar clima",
                "detalle": str(error),
                "temperatura": 0,
                "ciudad": "Error de conexión",
                "humedad": 0,
                "viento": 0,
                "lluvia": 0,
                "alertas": [],
            }
        ), 500