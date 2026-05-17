from datetime import datetime

from repositories.json_repository import filter_records
from services.weather_api_service import WeatherAPIService
from services.normalizer_service import normalizar_datos_aemet
from services.logging_service import log_info, log_error

def calculate_difference(v1, v2) -> float:
    try:
        val1 = float(v1) if v1 is not None else 0.0
        val2 = float(v2) if v2 is not None else 0.0
        return round(abs(val1 - val2), 2)
    except (ValueError, TypeError):
        return 0.0

def has_discrepancy(differences: dict) -> bool:
    return (
        differences["temperatura"] > 3 or
        differences["humedad"] > 10 or
        differences["viento"] > 10 or
        differences["lluvia"] > 5
    )


def _obtener_observacion_para_comparativa(
    api_service: WeatherAPIService,
    todas_las_obs: list,
    id_estacion: str,
    municipio: str,
):
    raw_api_data = next(
        (obs for obs in todas_las_obs if str(obs.get("idema")) == str(id_estacion)),
        None,
    )

    if raw_api_data:
        return raw_api_data

    municipio_aemet = api_service.municipality_service.obtener_municipio_por_nombre(
        municipio
    )

    if (
        not municipio_aemet
        or municipio_aemet.get("lat") is None
        or municipio_aemet.get("lon") is None
    ):
        return None

    return api_service.obtener_clima_por_coordenadas(
        municipio_aemet["lat"],
        municipio_aemet["lon"],
    )


def compare_latest_records(municipio: str, fecha_html: str = None) -> dict:
    """
    Orquestador de comparación. Filtra JSON por municipio/fecha y compara con API.
    """
    # 1. Normalizar la fecha (De AAAA-MM-DD a DD/MM/AAAA)
    if not fecha_html:
        fecha_target = datetime.now().strftime("%d/%m/%Y")
    else:
        try:
            fecha_obj = datetime.strptime(fecha_html, "%Y-%m-%d")
            fecha_target = fecha_obj.strftime("%d/%m/%Y")
        except ValueError:
            fecha_target = fecha_html

    log_info(f"Iniciando comparativa: {municipio} para el día {fecha_target}")

    # 2. Buscar registro manual en JSON
    # Usamos .title() para asegurar que coincida con el formato del JSON (Ej: 'Madrid')
    registros_hoy = filter_records(municipio=municipio.title(), fecha=fecha_target)
    manual_record = next((r for r in registros_hoy if r.get("fuente") == "manual"), None)
    
    if not manual_record:
        return {
            "success": False,
            "message": f"No hay datos manuales para {municipio} el día {fecha_target}."
        }

    id_estacion = manual_record.get("estacion_id")
    
    try:
        # 3. Consultar API AEMET
        api_service = WeatherAPIService()
        todas_las_obs = api_service.aemet_client.obtener_observaciones_actuales()

        if not isinstance(todas_las_obs, list):
            log_error(
                "AEMET devolvio observaciones con formato inesperado "
                f"en comparativa: {type(todas_las_obs).__name__}"
            )
            return {
                "success": False,
                "message": "AEMET no devolvio observaciones validas para comparar.",
            }
        
        raw_api_data = _obtener_observacion_para_comparativa(
            api_service=api_service,
            todas_las_obs=todas_las_obs,
            id_estacion=id_estacion,
            municipio=municipio,
        )
        
        if not raw_api_data:
            return {
                "success": False, 
                "message": (
                    f"AEMET no tiene datos actuales para la estacion {id_estacion} "
                    f"ni se pudo resolver una estacion cercana para {municipio}."
                )
            }

        api_record = normalizar_datos_aemet(raw_api_data)
        api_record["fuente"] = "AEMET (Oficial)"

    except Exception as e:
        log_error(f"Error en comparativa con AEMET: {e}")
        return {
            "success": False,
            "message": "No se pudo consultar AEMET para la comparativa.",
        }

    # 4. Calcular diferencias
    diffs = {
        "temperatura": calculate_difference(manual_record.get("temperatura"), api_record.get("temperatura")),
        "humedad":     calculate_difference(manual_record.get("humedad"), api_record.get("humedad")),
        "viento":      calculate_difference(manual_record.get("viento"), api_record.get("viento")),
        "lluvia":      calculate_difference(manual_record.get("lluvia"), api_record.get("lluvia"))
    }

    return {
        "success": True,
        "municipio": municipio.title(),
        "fecha": fecha_target,
        "manual": manual_record,
        "api": api_record,
        "diferencias": diffs,
        "hay_discrepancia": has_discrepancy(diffs)
    }
