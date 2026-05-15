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
5. Guardar un resumen del registro en SQL.
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

from db import crud
from db.database import SessionLocal, create_tables
from services.normalizer_service import normalizar_datos_aemet
from services.weather_api_service import obtener_clima_por_coordenadas


api_bp = Blueprint("api", __name__)

logger = logging.getLogger(__name__)


def _normalizar_cod_ine(codigo_municipio):
    if not codigo_municipio:
        return None

    codigo = str(codigo_municipio).strip()

    if codigo.startswith("id"):
        return codigo[2:]

    return codigo


def _guardar_resumen_en_sql(data):
    """
    Guarda solo los campos necesarios para el modelo SQL actual.

    Si falta información mínima para construir la zona, no bloquea la respuesta
    de la API: devuelve False y deja el aviso en logs.
    """

    municipio_detectado = data.get("municipio_detectado")
    if not isinstance(municipio_detectado, dict):
        municipio_detectado = {}

    cod_ine = _normalizar_cod_ine(
        municipio_detectado.get("codigo") or data.get("codigo_municipio")
    )

    id_estacion = data.get("id_estacion")

    if not cod_ine or not id_estacion:
        logger.warning(
            "No se guarda medición en SQL: faltan cod_ine o id_estacion. "
            "cod_ine=%s id_estacion=%s",
            cod_ine,
            id_estacion,
        )
        return False

    create_tables()
    db = SessionLocal()

    try:
        zona = crud.obtener_zona_por_cod_ine(db=db, cod_ine=cod_ine)

        if zona is None:
            zona = crud.crear_zona(
                db=db,
                zona_data={
                    "municipio": (
                        municipio_detectado.get("nombre")
                        or data.get("municipio")
                        or data.get("ciudad")
                        or "Ubicación detectada"
                    ),
                    "cod_ine": cod_ine,
                    "id_estacion": str(id_estacion),
                    "estacion_referencia": data.get("estacion") or str(id_estacion),
                },
            )

        medicion = crud.crear_medicion(
            db=db,
            zona_id=zona.id,
            medicion_data={
                "fecha_datos": data.get("fecha") or "fecha_no_disponible",
                "temperatura": data.get("temperatura"),
                "humedad": data.get("humedad"),
                "viento": data.get("viento"),
                "lluvia": data.get("lluvia"),
            },
        )

        return medicion is not None

    except Exception:
        db.rollback()
        logger.exception("No se pudo guardar el registro climático en SQL.")
        return False

    finally:
        db.close()


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
        # 5. Guardar resumen del registro en SQL
        # ---------------------------------------------------------
        #
        # Si el guardado falla, no rompemos la respuesta al usuario.
        # Solo añadimos una advertencia.
        guardado_correcto = _guardar_resumen_en_sql(data)

        if not guardado_correcto:
            logger.warning("No se pudo guardar el registro climático en SQL.")
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
                "temperatura": None,
                "ciudad": "Error de conexión",
                "humedad": None,
                "viento": None,
                "lluvia": None,
                "alertas": [],
            }
        ), 500
