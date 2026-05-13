# services/normalizer_service.py

"""
Normalizador de datos meteorológicos.

Este archivo transforma los datos crudos de AEMET en un formato limpio
y fácil de usar por el frontend.

AEMET devuelve campos técnicos como:

- "ta"   -> temperatura del aire
- "hr"   -> humedad relativa
- "vv"   -> velocidad del viento
- "dv"   -> dirección del viento
- "vmax" -> racha máxima de viento
- "pres" -> presión
- "prec" -> precipitación / lluvia
- "ubi"  -> ubicación de la estación
- "fint" -> fecha/hora de la observación

Nosotros los convertimos a campos más claros:

- temperatura
- humedad
- viento
- lluvia
- estacion
- municipio
- prediccion_diaria
- prediccion_horaria
"""

import logging
from typing import Any, Dict, List, Optional

from services.alert_service import AlertService


# Servicio existente para generar alertas climáticas.
alert_service = AlertService()


def normalizar_datos_aemet(data: Any) -> Dict[str, Any]:
    """
    Transforma los datos crudos de AEMET en un formato estándar.

    Esta función es usada directamente por:
        controllers/api_controller.py

    Recibe:
        - datos de la estación AEMET más cercana,
        - municipio detectado,
        - predicción diaria,
        - predicción horaria.

    Devuelve:
        Un diccionario limpio para el frontend.
    """

    try:
        if not data:
            return _respuesta_sin_datos()

        latest = _obtener_ultimo_registro(data)

        if not isinstance(latest, dict):
            return _respuesta_sin_datos()

        # -------------------------------------------------------------
        # Datos básicos de la estación AEMET
        # -------------------------------------------------------------

        nombre_lugar = (
            latest.get("ubi")
            or latest.get("estacion")
            or latest.get("nombre")
            or latest.get("municipio")
            or "Ubicación detectada"
        )

        fecha_observacion = (
            latest.get("fint")
            or latest.get("fecha")
            or latest.get("fhora")
            or "N/A"
        )

        temperatura = _to_float(latest.get("ta"), default=0.0)
        humedad = _to_float(latest.get("hr"), default=0.0)
        viento = _to_float(latest.get("vv"), default=0.0)
        presion = _to_float(latest.get("pres"), default=0.0)
        lluvia = _parse_precipitacion(latest.get("prec"))

        direccion_viento = _to_float_or_none(latest.get("dv"))
        racha_viento = _to_float_or_none(latest.get("vmax"))

        distancia_estacion_km = _to_float_or_none(
            latest.get("distancia_estacion_km")
        )

        lat_usuario = _to_float_or_none(latest.get("lat_usuario"))
        lon_usuario = _to_float_or_none(latest.get("lon_usuario"))

        lat_estacion = _to_float_or_none(latest.get("lat"))
        lon_estacion = _to_float_or_none(latest.get("lon"))

        # -------------------------------------------------------------
        # Datos nuevos: municipio y predicción
        # -------------------------------------------------------------

        municipio_detectado = _normalizar_municipio(
            latest.get("municipio_detectado")
        )

        codigo_municipio = latest.get("codigo_municipio")

        prediccion_diaria_raw = latest.get("prediccion_diaria")
        prediccion_horaria_raw = latest.get("prediccion_horaria")

        resumen_prediccion_diaria = _extraer_resumen_prediccion_diaria(
            prediccion_diaria_raw
        )

        resumen_prediccion_horaria = _extraer_resumen_prediccion_horaria(
            prediccion_horaria_raw
        )

        # -------------------------------------------------------------
        # Respuesta final para frontend
        # -------------------------------------------------------------

        datos_normalizados = {
            # ---------------------------------------------------------
            # Campos que ya existían y que no conviene romper
            # ---------------------------------------------------------
            "ciudad": nombre_lugar,
            "estacion": nombre_lugar,
            "fecha": fecha_observacion,
            "temperatura": temperatura,
            "humedad": humedad,
            "viento": viento,
            "presion": presion,
            "lluvia": lluvia,

            # ---------------------------------------------------------
            # Información de estación
            # ---------------------------------------------------------
            "id_estacion": latest.get("idema"),
            "distancia_estacion_km": distancia_estacion_km,

            "coordenadas_usuario": {
                "lat": lat_usuario,
                "lon": lon_usuario,
            },

            "coordenadas_estacion": {
                "lat": lat_estacion,
                "lon": lon_estacion,
            },

            # ---------------------------------------------------------
            # Información detallada de viento
            # ---------------------------------------------------------
            "viento_detalle": {
                "velocidad": viento,
                "direccion": direccion_viento,
                "racha_maxima": racha_viento,
            },

            # ---------------------------------------------------------
            # Información del municipio AEMET detectado
            # ---------------------------------------------------------
            "municipio_detectado": municipio_detectado,
            "codigo_municipio": codigo_municipio,

            # ---------------------------------------------------------
            # Predicción procesada para pintar fácil en el frontend
            # ---------------------------------------------------------
            "prediccion": {
                "diaria": resumen_prediccion_diaria,
                "horaria": resumen_prediccion_horaria,
            },

            # ---------------------------------------------------------
            # Predicción cruda por si más adelante necesitamos más campos
            # ---------------------------------------------------------
            "prediccion_raw": {
                "diaria": prediccion_diaria_raw,
                "horaria": prediccion_horaria_raw,
            },

            "fuente_original": "AEMET",
        }

        # Generamos alertas con el servicio existente.
        datos_normalizados["alertas"] = alert_service.evaluar_alertas(
            datos_normalizados
        )

        return datos_normalizados

    except Exception as error:
        logging.error("Error en normalización AEMET: %s", error)

        return {
            "error": "Error al procesar los datos de AEMET",
            "ciudad": "Error",
            "estacion": "Error",
            "fecha": "N/A",
            "temperatura": 0,
            "humedad": 0,
            "viento": 0,
            "presion": 0,
            "lluvia": 0,
            "alertas": [],
        }


# ---------------------------------------------------------------------
# FUNCIONES AUXILIARES GENERALES
# ---------------------------------------------------------------------

def _obtener_ultimo_registro(data: Any) -> Any:
    """
    Si data es una lista, devuelve el último elemento.

    Si data ya es un diccionario, lo devuelve tal cual.
    """

    if isinstance(data, list):
        if not data:
            return None

        return data[-1]

    return data


def _to_float(valor: Any, default: float = 0.0) -> float:
    """
    Convierte un valor a float de forma segura.

    Si no se puede convertir, devuelve default.
    """

    if valor is None:
        return default

    try:
        if isinstance(valor, str):
            valor = valor.strip().replace(",", ".")

            if valor == "":
                return default

        return float(valor)

    except (ValueError, TypeError):
        return default


def _to_float_or_none(valor: Any) -> Optional[float]:
    """
    Convierte un valor a float.

    Si no se puede convertir, devuelve None.
    """

    if valor is None:
        return None

    try:
        if isinstance(valor, str):
            valor = valor.strip().replace(",", ".")

            if valor == "":
                return None

        return float(valor)

    except (ValueError, TypeError):
        return None


def _parse_precipitacion(valor: Any) -> float:
    """
    Convierte el campo de precipitación de AEMET a número.

    AEMET puede devolver "Ip" o "IP" para indicar precipitación inapreciable.
    Para la app lo convertimos a 0.0.
    """

    if valor is None:
        return 0.0

    if isinstance(valor, str):
        valor_limpio = valor.strip().replace(",", ".")

        if valor_limpio.lower() in {"ip", "tr", ""}:
            return 0.0

        try:
            return float(valor_limpio)

        except ValueError:
            return 0.0

    try:
        return float(valor)

    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------
# MUNICIPIO
# ---------------------------------------------------------------------

def _normalizar_municipio(municipio: Any) -> Optional[Dict[str, Any]]:
    """
    Normaliza el municipio detectado por MunicipalityService.

    Esperamos algo como:

    {
        "codigo": "id28079",
        "nombre": "Madrid",
        "provincia": "Madrid",
        "lat": 40.4167,
        "lon": -3.7033,
        "distancia_km": 1.25,
        "raw": {...}
    }
    """

    if not isinstance(municipio, dict):
        return None

    return {
        "codigo": municipio.get("codigo"),
        "nombre": municipio.get("nombre"),
        "provincia": municipio.get("provincia"),
        "lat": _to_float_or_none(municipio.get("lat")),
        "lon": _to_float_or_none(municipio.get("lon")),
        "distancia_km": _to_float_or_none(municipio.get("distancia_km")),
    }


# ---------------------------------------------------------------------
# PREDICCIÓN DIARIA
# ---------------------------------------------------------------------

def _extraer_resumen_prediccion_diaria(prediccion: Any) -> Optional[Dict[str, Any]]:
    """
    Extrae un resumen sencillo de la predicción diaria de AEMET.

    AEMET puede devolver:

    [
        {
            "nombre": "Madrid",
            "provincia": "Madrid",
            "prediccion": {
                "dia": [
                    {
                        "fecha": "...",
                        "temperatura": {
                            "maxima": 20,
                            "minima": 10
                        },
                        "probPrecipitacion": [...],
                        "estadoCielo": [...],
                        "viento": [...]
                    }
                ]
            }
        }
    ]

    Esta función intenta devolver algo fácil de consumir:

    {
        "municipio": "Madrid",
        "provincia": "Madrid",
        "dias": [...]
    }
    """

    prediccion_obj = _obtener_objeto_prediccion(prediccion)

    if not prediccion_obj:
        return None

    dias = (
        prediccion_obj
        .get("prediccion", {})
        .get("dia", [])
    )

    if not isinstance(dias, list):
        dias = []

    dias_normalizados = []

    for dia in dias:
        if not isinstance(dia, dict):
            continue

        temperatura = dia.get("temperatura", {})

        dias_normalizados.append(
            {
                "fecha": dia.get("fecha"),
                "temperatura_maxima": _to_float_or_none(
                    temperatura.get("maxima")
                    if isinstance(temperatura, dict)
                    else None
                ),
                "temperatura_minima": _to_float_or_none(
                    temperatura.get("minima")
                    if isinstance(temperatura, dict)
                    else None
                ),
                "probabilidad_precipitacion": _extraer_primer_valor(
                    dia.get("probPrecipitacion")
                ),
                "estado_cielo": _extraer_descripcion_estado_cielo(
                    dia.get("estadoCielo")
                ),
                "viento": _extraer_viento_diario(dia.get("viento")),
                "uv_max": _to_float_or_none(dia.get("uvMax")),
            }
        )

    return {
        "municipio": prediccion_obj.get("nombre"),
        "provincia": prediccion_obj.get("provincia"),
        "elaborado": prediccion_obj.get("elaborado"),
        "dias": dias_normalizados,
    }


# ---------------------------------------------------------------------
# PREDICCIÓN HORARIA
# ---------------------------------------------------------------------

def _extraer_resumen_prediccion_horaria(prediccion: Any) -> Optional[Dict[str, Any]]:
    """
    Extrae un resumen sencillo de la predicción horaria.

    La predicción horaria de AEMET suele incluir arrays con datos por hora:
    - temperatura
    - estadoCielo
    - precipitacion
    - probPrecipitacion
    - vientoAndRachaMax
    - humedadRelativa
    - sensTermica

    Aquí devolvemos una versión resumida para que el frontend pueda pintar
    las próximas horas.
    """

    prediccion_obj = _obtener_objeto_prediccion(prediccion)

    if not prediccion_obj:
        return None

    dias = (
        prediccion_obj
        .get("prediccion", {})
        .get("dia", [])
    )

    if not isinstance(dias, list):
        dias = []

    dias_normalizados = []

    for dia in dias:
        if not isinstance(dia, dict):
            continue

        dias_normalizados.append(
            {
                "fecha": dia.get("fecha"),
                "temperatura": _normalizar_lista_periodos(
                    dia.get("temperatura")
                ),
                "precipitacion": _normalizar_lista_periodos(
                    dia.get("precipitacion")
                ),
                "probabilidad_precipitacion": _normalizar_lista_periodos(
                    dia.get("probPrecipitacion")
                ),
                "estado_cielo": _normalizar_estado_cielo_horario(
                    dia.get("estadoCielo")
                ),
                "humedad_relativa": _normalizar_lista_periodos(
                    dia.get("humedadRelativa")
                ),
                "sensacion_termica": _normalizar_lista_periodos(
                    dia.get("sensTermica")
                ),
                "viento_y_rachas": dia.get("vientoAndRachaMax"),
            }
        )

    return {
        "municipio": prediccion_obj.get("nombre"),
        "provincia": prediccion_obj.get("provincia"),
        "elaborado": prediccion_obj.get("elaborado"),
        "dias": dias_normalizados,
    }


def _obtener_objeto_prediccion(prediccion: Any) -> Optional[Dict[str, Any]]:
    """
    AEMET puede devolver predicción como dict o como lista.

    Esta función devuelve siempre un dict si puede.
    """

    if isinstance(prediccion, dict):
        return prediccion

    if isinstance(prediccion, list) and prediccion:
        primer_elemento = prediccion[0]

        if isinstance(primer_elemento, dict):
            return primer_elemento

    return None


def _extraer_primer_valor(lista: Any) -> Optional[Any]:
    """
    Extrae el primer valor útil de una lista de AEMET.

    Muchos campos de AEMET vienen así:

    [
        {"value": 10, "periodo": "00-24"}
    ]

    Devolvemos el primer "value".
    """

    if not isinstance(lista, list) or not lista:
        return None

    primer = lista[0]

    if isinstance(primer, dict):
        return primer.get("value")

    return primer


def _extraer_descripcion_estado_cielo(lista: Any) -> Optional[str]:
    """
    Extrae una descripción de estado del cielo.

    AEMET puede devolver:
    [
        {
            "value": "12",
            "periodo": "00-24",
            "descripcion": "Poco nuboso"
        }
    ]
    """

    if not isinstance(lista, list) or not lista:
        return None

    for item in lista:
        if isinstance(item, dict):
            descripcion = item.get("descripcion")

            if descripcion:
                return descripcion

    return None


def _extraer_viento_diario(viento: Any) -> Optional[Dict[str, Any]]:
    """
    Extrae un resumen del viento diario.

    AEMET puede devolver:
    [
        {
            "direccion": "N",
            "velocidad": 10,
            "periodo": "00-24"
        }
    ]
    """

    if not isinstance(viento, list) or not viento:
        return None

    primer = viento[0]

    if not isinstance(primer, dict):
        return None

    return {
        "direccion": primer.get("direccion"),
        "velocidad": _to_float_or_none(primer.get("velocidad")),
        "periodo": primer.get("periodo"),
    }


def _normalizar_lista_periodos(lista: Any) -> List[Dict[str, Any]]:
    """
    Normaliza listas horarias de AEMET.

    Convierte datos como:

    [
        {"value": 18, "periodo": "10"},
        {"value": 19, "periodo": "11"}
    ]

    en una lista limpia.
    """

    if not isinstance(lista, list):
        return []

    resultado = []

    for item in lista:
        if not isinstance(item, dict):
            continue

        resultado.append(
            {
                "periodo": item.get("periodo"),
                "valor": item.get("value"),
            }
        )

    return resultado


def _normalizar_estado_cielo_horario(lista: Any) -> List[Dict[str, Any]]:
    """
    Normaliza el estado del cielo por horas.
    """

    if not isinstance(lista, list):
        return []

    resultado = []

    for item in lista:
        if not isinstance(item, dict):
            continue

        resultado.append(
            {
                "periodo": item.get("periodo"),
                "valor": item.get("value"),
                "descripcion": item.get("descripcion"),
            }
        )

    return resultado


def _respuesta_sin_datos() -> Dict[str, Any]:
    """
    Respuesta estándar cuando no hay datos disponibles.

    Así evitamos errores en el frontend.
    """

    return {
        "error": "No hay datos disponibles",
        "ciudad": "Ubicación no disponible",
        "estacion": "Ubicación no disponible",
        "fecha": "N/A",
        "temperatura": 0,
        "humedad": 0,
        "viento": 0,
        "presion": 0,
        "lluvia": 0,
        "distancia_estacion_km": None,
        "coordenadas_usuario": {
            "lat": None,
            "lon": None,
        },
        "coordenadas_estacion": {
            "lat": None,
            "lon": None,
        },
        "viento_detalle": {
            "velocidad": 0,
            "direccion": None,
            "racha_maxima": None,
        },
        "municipio_detectado": None,
        "codigo_municipio": None,
        "prediccion": {
            "diaria": None,
            "horaria": None,
        },
        "prediccion_raw": {
            "diaria": None,
            "horaria": None,
        },
        "fuente_original": "AEMET",
        "alertas": [],
    }