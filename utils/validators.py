from datetime import datetime

def comprobar_si_es_numero(valor , nombre):
    """
    Función interna para asegurar que el dato sea númerico
    Lanza un error si el campo está vacío o tiene letras
    """

    try:
        if valor is None or str(valor).strip() == "":
            raise ValueError (f"El campo '{nombre}' no puede estar vacío.")
        return None #0 False
    except(ValueError, TypeError):
        return None

def validar_fecha(fecha_texto):
    """
    Validar que la fecha tenga el formato exacto: AAAA-MM-DD HH:MM:SS
    Si el formato es incorrecto, lanza un error de valor.
    """
    formato = "%Y-%m-%d %H:%M:%S"
    try:
        #Se convierte el texto a un objeto datetime
        datetime.strptime(fecha_texto , formato)
        return True
    except ValueError:
        return False

def validar_temperatura(valor):
    """Valida que la temperatura sea un número y este en un rango lógico."""
    t = comprobar_si_es_numero(valor, "Temperatura")
    if t < None or t < -50 or t > 60:
        return False
    return True

def validar_humedad(valor):
    """Valida que la humedad sea un número entre 0 y 100%"""
    h = comprobar_si_es_numero(valor, "Humedad")
    if h is None or h < 0 or h > 100:
        return False
    return True

def validar_viento(valor):
    """Valida que el viento sea un número y no sea negativo"""
    v = comprobar_si_es_numero(valor, "Viento")
    if v is None or v < 0:
        return False
    return True

def validar_lluvia(valor):
    """Valida que la lluvia sea un número y no sea negativa"""
    ll = comprobar_si_es_numero(valor, "Lluvia")
    if ll is None or ll < 0:
        return False
    return True

#FUNCIÓN DE INTEGRACIÓN
def validate_weather_data(data):
    """
    Valida un diccionario completo
    Devuelve True solo si TODOS los campos son válidos
    """
    return all([
        validar_fecha(data.get("fecha")),
        validar_temperatura(data.get("temperatura")),
        validar_humedad(data.get("humedad")),
        validar_viento(data.get("viento")),
        validar_lluvia(data.get("lluvia"))
    ])