import logging
from typing import Dict, Any, List

try:
    from utils.validators import validate_weather_data
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("No se pudo importar 'validate_weather_data'. Usando validador temporal.")

    def validate_weather_data(data: Dict[str, Any]) -> bool:
        return True


class AlertService:
    """Motor de análisis de riesgos climáticos y generación de alertas."""

    def evaluar_alertas(self, registro_normalizado: Dict[str, Any]) -> List[str]:

        if not validate_weather_data(registro_normalizado):
            return []

        alertas = []

# Obtenemos los valores del registro normalizado
# IMPORTANTE: no convertimos None a 0 porque según la política del equipo
# los datos faltantes se deben ignorar, no sustituir


        temp = registro_normalizado.get("temperatura")
        viento = registro_normalizado.get("viento")
        lluvia = registro_normalizado.get("lluvia")
        humedad = registro_normalizado.get("humedad")


        # =========================
        # TEMPERATURA
        # =========================
        # Solo evaluamos si el dato existe (no es None)
        if temp is not None:
            temp = float(temp)


            if temp >= 40.0:
                alertas.append("ROJA_CALOR")
            elif temp >= 35.0:
                alertas.append("NARANJA_CALOR")
            elif temp <= -5.0:
                alertas.append("ROJA_FRIO")
            elif temp <= 0.0:
                alertas.append("NARANJA_FRIO")

        # =========================
        # VIENTO
        # =========================
        # Solo evaluamos si el dato existe (no es None)
        if viento is not None:
            viento = float(viento)

            if viento > 70.0:
                alertas.append("ROJA_VIENTO")
        
            elif viento > 40.0:
                alertas.append("NARANJA_VIENTO")

        # =========================
        # LLUVIA
        # =========================
        # Solo evaluamos si el dato existe (no es None)

        if lluvia is not None:
            lluvia = float(lluvia)

            if lluvia > 30.0:
                alertas.append("ROJA_LLUVIA")
            elif lluvia > 10.0:
                alertas.append("NARANJA_LLUVIA")

        # =========================
        # HUMEDAD
        # =========================
        # Solo evaluamos si el dato existe (no es None)
        if humedad is not None:
            humedad = float(humedad)

            if humedad >= 90:
                alertas.append("NARANJA_HUMEDAD")

        # Si no hay ningún dato meteorológico, no generamos alerta.
        if temp is None and viento is None and lluvia is None and humedad is None:
            return []

        # Si hay datos pero no hay riesgo, devolvemos estado verde.
        if not alertas:
            alertas.append("VERDE")

        return alertas