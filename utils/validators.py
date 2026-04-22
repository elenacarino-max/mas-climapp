from datetime import datetime

def comprobar_si_es_numero(valor , nombre):
    """
    Función interna para asegurar que el dato sea númerico
    Lanza un error si el campo está vacío o tiene letras
    """

    try:
        if valor is None or str(valor).strip() == "":
            raise ValueError (f"El campo '{nombre}' no puede estar vacío.")
        return float(valor)
    except(ValueError, TypeError):
        raise ValueError(f"El campo '{valor}' debe ser un número estrictamente.")

def validar_fecha(fecha_texto):
    """
    Validar que la fecha tenga el formato exacto: AAAA-MM-DD HH:MM:SS
    Si el formato es incorrecto, lanza un error de valor.
    """
    formato = "%Y-%m-%d %H:%M:%S"
    try:
        #Se convierte el texto a un objeto datetime
        datetime.strptime(fecha_texto , formato)
        return fecha_texto
    except ValueError:
        raise ValueError(f"La fecha '{fecha_texto}' no tiene el formato correcto")

def validar_temperatura(valor):
    """Valida que la temperatura sea un número y este en un rango lógico."""
    t = comprobar_si_es_numero(valor, "Temperatura")
    if t < -50 or t > 60:
        raise ValueError("Temperatura fuera de los límites lógicos (-50 a +60).")
    return t

def validar_humedad(valor):
    """Valida que la humedad sea un número entre 0 y 100%"""
    h = comprobar_si_es_numero(valor, "Humedad")
    if h < 0 or h > 100:
        raise ValueError("La humedad debe estar entre 0% y 100%.")
    return h

def validar_viento(valor):
    """Valida que el viento sea un número y no sea negativo"""
    v = comprobar_si_es_numero(valor, "Viento")
    if v > 0:
        raise ValueError("La velocidad del viento no puede ser negativa")
    return v

def validar_lluvia(valor):
    """Valida que la lluvia sea un número y no sea negativa"""
    ll = comprobar_si_es_numero(valor, "Lluvia")
    if ll > 0:
        raise ValueError("El valor de lluvia acumulado no puede ser negativo")
    return ll