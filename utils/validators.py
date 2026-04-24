import datetime #Importación de modulo para manejo de fechas

def comprobar_si_es_numero(valor , nombre):
    """
    Intenta convertir una entrada a float
    Retorna el valor númerico si es exitoso, o None si el valor está vacío 
    o no es convertible
    """

    try:
        if valor is None or str(valor).strip() == "":
            return None
    # Conversión explícita para habilitar validaciones de rango 
    except(ValueError, TypeError):
        return None

def validar_fecha(fecha_texto):
    """
    Verifica si una cadena de texto cumple con el formato
    estándar AAAA-MM-DD HH:MM:SS
    """
    formato = "%Y-%m-%d %H:%M:%S"
    try:
        datetime.datetime.strptime(fecha_texto , formato)
        return True
    except ValueError:
        return False

def validar_temperatura(valor):
    """
    Comprueba si la temperatura es un número válido
    dentro del rango físico de -50 a 60 grados.
    """
    t = comprobar_si_es_numero(valor, "Temperatura")
    # Se valida que no sea None antes de comparar rangos
    if t is None or t < -50 or t > 60:
        return False
    return True

def validar_humedad(valor):
    """Valida que la humedad sea un valor númerico
    comprendido entre 0 y 100 por ciento
    """
    h = comprobar_si_es_numero(valor, "Humedad")
    if h is None or h < 0 or h > 100:
        return False
    return True

def validar_viento(valor):
    """Asegura que la velocidad del viento sea un número y 
    que no presente valores negativos
    """
    v = comprobar_si_es_numero(valor, "Viento")
    if v is None or v < 0:
        return False
    return True

def validar_lluvia(valor):
    """Verifica que la precipitación sea un número válido
    y que no sea inferior a cero"""
    ll = comprobar_si_es_numero(valor, "Lluvia")
    if ll is None or ll < 0:
        return False
    return True

#FUNCIÓN DE INTEGRACIÓN
def validate_weather_data(data):
    """
    Realiza una validación integral de un diccionario de daots.
    Retorna True si todos los párametros climáticos son correctos
    """
    return all([
        validar_fecha(data.get("fecha")),
        validar_temperatura(data.get("temperatura")),
        validar_humedad(data.get("humedad")),
        validar_viento(data.get("viento")),
        validar_lluvia(data.get("lluvia"))
    ])