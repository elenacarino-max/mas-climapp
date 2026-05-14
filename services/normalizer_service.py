# services/normalizer_service.py

import logging
from typing import Any, Dict, List, Optional

from services.alert_service import AlertService


alert_service = AlertService()
logger = logging.getLogger(__name__)


def normalizar_datos_aemet(data: Any) -> Dict[str, Any]:
    """
    Transforma los datos crudos de AEMET en un formato estándar.
    """

    try:
        if not data:
            return _respuesta_sin_datos()

        latest = _obtener_ultimo_registro(data)

        if not isinstance(latest, dict):
            return _respuesta_sin_datos()

        nombre_lugar = (
            latest.get("ubi")
            or latest.get("estacion")
            or latest.get("nombre")
            or latest.get("municipio")
            or "Ubicación Desconocida"
        )

        fecha_observacion = (
            latest.get("fint")
            or latest.get("fecha")
            or latest.get("fhora")
        )

        temperatura = _to_float_or_none(latest.get("ta"))
        humedad = _to_float_or_none(latest.get("hr"))
        viento = _to_float_or_none(latest.get("vv"))
        presion = _to_float_or_none(latest.get("pres"))
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

        datos_normalizados = {
            "ciudad": nombre_lugar,
            "estacion": nombre_lugar,
            "fecha": fecha_observacion,
            "temperatura": temperatura,
            "humedad": humedad,
            "viento": viento,
            "presion": presion,
            "lluvia": lluvia,

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

            "viento_detalle": {
                "velocidad": viento,
                "direccion": direccion_viento,
                "racha_maxima": racha_viento,
            },

            "municipio_detectado": municipio_detectado,
            "codigo_municipio": codigo_municipio,

            "prediccion": {
                "diaria": resumen_prediccion_diaria,
                "horaria": resumen_prediccion_horaria,
            },

            "prediccion_raw": {
                "diaria": prediccion_diaria_raw,
                "horaria": prediccion_horaria_raw,
            },

            "fuente_original": "AEMET",
        }

        datos_normalizados["alertas"] = _evaluar_alertas_seguro(
            datos_normalizados
        )

        return datos_normalizados

    except (TypeError, ValueError, AttributeError, KeyError) as error:
        logger.error("Error en normalización AEMET: %s", error)
        return _respuesta_error_normalizacion()


# ---------------------------------------------------------------------
# FUNCIONES AUXILIARES GENERALES
# ---------------------------------------------------------------------

def _obtener_ultimo_registro(data: Any) -> Any:
    if isinstance(data, list):
        if not data:
            return None

        return data[-1]

    return data


def _to_float_or_none(valor: Any) -> Optional[float]:
    """
    Convierte un valor a float.

    Si no se puede convertir, devuelve None.
    Así diferenciamos entre:
    - dato no disponible: None
    - dato real cero: 0.0
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


def _parse_precipitacion(valor: Any) -> Optional[float]:
    """
    Convierte precipitación.

    Importante:
    - None significa dato no disponible.
    - 0.0 significa valor real cero o precipitación inapreciable.
    """

    if valor is None:
        return None

    if isinstance(valor, str):
        valor_limpio = valor.strip().replace(",", ".")

        if valor_limpio == "":
            return None

        if valor_limpio.lower() in {"ip", "tr"}:
            return 0.0

        try:
            return float(valor_limpio)

        except ValueError:
            return None

    try:
        return float(valor)

    except (ValueError, TypeError):
        return None


def _evaluar_alertas_seguro(datos: Dict[str, Any]) -> List[Any]:
    """
    Evalúa alertas sin romper la normalización.

    Si AlertService todavía no soporta None en algún campo,
    devolvemos lista vacía y dejamos log claro.
    """

    try:
        return alert_service.evaluar_alertas(datos)

    except (TypeError, ValueError, AttributeError) as error:
        logger.warning("No se pudieron evaluar alertas: %s", error)
        return []


# ---------------------------------------------------------------------
# MUNICIPIO
# ---------------------------------------------------------------------

def _normalizar_municipio(municipio: Any) -> Optional[Dict[str, Any]]:
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
    if isinstance(prediccion, dict):
        return prediccion

    if isinstance(prediccion, list) and prediccion:
        primer_elemento = prediccion[0]

        if isinstance(primer_elemento, dict):
            return primer_elemento

    return None


def _extraer_primer_valor(lista: Any) -> Optional[Any]:
    if not isinstance(lista, list) or not lista:
        return None

    primer = lista[0]

    if isinstance(primer, dict):
        return primer.get("value")

    return primer


def _extraer_descripcion_estado_cielo(lista: Any) -> Optional[str]:
    if not isinstance(lista, list) or not lista:
        return None

    for item in lista:
        if isinstance(item, dict):
            descripcion = item.get("descripcion")

            if descripcion:
                return descripcion

    return None


def _extraer_viento_diario(viento: Any) -> Optional[Dict[str, Any]]:
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
    return {
        "error": "No hay datos disponibles",
        "ciudad": "Ubicación no disponible",
        "estacion": "Ubicación no disponible",
        "fecha": None,
        "temperatura": None,
        "humedad": None,
        "viento": None,
        "presion": None,
        "lluvia": None,
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
            "velocidad": None,
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


def _respuesta_error_normalizacion() -> Dict[str, Any]:
    return {
        "error": "Error al procesar los datos de AEMET",
        "ciudad": "Error",
        "estacion": "Error",
        "fecha": None,
        "temperatura": None,
        "humedad": None,
        "viento": None,
        "presion": None,
        "lluvia": None,
        "alertas": [],
    }