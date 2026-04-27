from services.alert_service import AlertService

# Prueba manual extrema
servicio = AlertService()
datos_sucios = {"temperatura": "42.5", "viento": None, "lluvia": "mucha"} 

try:
    resultado = servicio.evaluar_alertas(datos_sucios)
    print(f"✅ Prueba superada. Resultado: {resultado}")
except Exception as e:
    print(f"❌ Falló: {e}")