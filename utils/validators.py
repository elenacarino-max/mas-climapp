import datetime

def comprobar_si_es_numero(valor, nombre):
    """
    Isabella, corregido: ahora devuelve el float para validar rangos.
    """
    try:
        if valor is None or str(valor).strip() == "":
            return None
        return float(valor)
    except (ValueError, TypeError):
        return None

def validar_fecha(fecha_texto):
    """
    CAMBIO MÍO: He adaptado la función para que acepte el formato 
    que configuramos en el JS (DD/MM/AAAA) y sea flexible con otros.
    """
    if not fecha_texto: 
        return False
    
    # Limpiamos posibles restos de hora o formatos ISO
    fecha_texto = fecha_texto.replace('T', ' ').split(' ')[0]
    
    # Lista de formatos sin hora (ya que la hemos quitado en el HTML/JS)
    formatos_a_probar = [
        "%d/%m/%Y",  # Formato actual: 29/04/2026
        "%d-%m-%Y",  # Alternativa con guiones
        "%Y-%m-%d"   # Formato ISO por si acaso
    ]
    
    for formato in formatos_a_probar:
        try:
            datetime.datetime.strptime(fecha_texto, formato)
            return True
        except ValueError:
            continue
            
    return False

def validar_temperatura(valor):
    t = comprobar_si_es_numero(valor, "Temperatura")
    return t is not None and -50 <= t <= 60

def validar_humedad(valor):
    h = comprobar_si_es_numero(valor, "Humedad")
    return h is not None and 0 <= h <= 100

def validar_viento(valor):
    v = comprobar_si_es_numero(valor, "Viento")
    return v is not None and v >= 0

def validar_lluvia(valor):
    ll = comprobar_si_es_numero(valor, "Lluvia")
    return ll is not None and ll >= 0

# --- FUNCIÓN DE INTEGRACIÓN ---
def validate_weather_data(data):

    """
    Valida un registro climático completo.

    Política aplicada:
    - La fecha es obligatoria.
    - Los datos meteorológicos (temperatura, humedad, viento, lluvia) son opcionales.
    - Si un campo viene con valor → se valida.
    - Si un campo viene como None → se ignora (no se considera error).
    """
        
    # Comprobamos que el input sea válido
    if not data or not isinstance(data, dict):
        return False

    return (
        # Campo obligatorio: la fecha debe existir y ser válida
        validar_fecha(data.get("fecha_datos"))

        # Campos opcionales:
        # Si hay valor → validamos
        # Si es None → lo aceptamos (no se sustituye por 0 según la política del equipo)

        and (data.get("temperatura") is None or validar_temperatura(data.get("temperatura")))
        and (data.get("humedad") is None or validar_humedad(data.get("humedad")))
        and (data.get("viento") is None or validar_viento(data.get("viento")))
        and (data.get("lluvia") is None or validar_lluvia(data.get("lluvia")))
    )