import os
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
        todas_las_obs = api_service._obtener_datos_crudos()
        
        raw_api_data = next(
            (obs for obs in todas_las_obs if str(obs.get('idema')) == str(id_estacion)), 
            None
        )
        
        if not raw_api_data:
            return {
                "success": False, 
                "message": f"La AEMET no tiene datos hoy para la estación {id_estacion}."
            }

        api_record = normalizar_datos_aemet(raw_api_data)
        api_record["fuente"] = "AEMET (Oficial)"

    except Exception as e:
        log_error(f"Error en comparativa: {e}")
        return {"success": False, "message": "Error de conexión con la API de AEMET."}

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