import logging

def normalizar_datos_aemet(data):
    """
    Transforma los datos crudos de AEMET en un formato estándar.
    """
    try:
        if not data:
            return {"error": "No hay datos disponibles"}

        # Si es una lista, tomamos el último registro (el más reciente)
        latest = data[-1] if isinstance(data, list) else data
        
        # Mapeo de nombres crípticos a nombres claros
        return {
            "estacion": latest.get("ubi", "Desconocida"),
            "fecha": latest.get("fint", "N/A"),
            "temperatura": float(latest.get("ta", 0)) if latest.get("ta") else 0,
            "humedad": float(latest.get("hr", 0)) if latest.get("hr") else 0,
            "viento": float(latest.get("vv", 0)) if latest.get("vv") else 0,
            "presion": float(latest.get("pres", 0)) if latest.get("pres") else 0
        }

    except Exception as e:
        logging.error(f"Error en normalización: {e}")
        return {"error": "Error al procesar los datos"}