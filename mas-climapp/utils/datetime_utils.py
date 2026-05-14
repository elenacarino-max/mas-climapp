import datetime


def validar_fecha(fecha_texto):
    """
    🔹 Función para validar fechas en distintos formatos.

    Acepta:
    - "29/04/2026"  (formato español)
    - "29-04-2026"  (con guiones)
    - "2026-04-29"  (formato ISO)
    - "2026-04-29T14:30" (formato API con hora)

    🔹 Devuelve:
    - True → si la fecha es válida
    - False → si no lo es
    """

    # ❗ Si no viene nada, no es válido
    if not fecha_texto:
        return False

    # 🔧 Convertimos a string por seguridad (por si viene otro tipo)
    fecha_texto = str(fecha_texto)

    # 🔧 Limpiamos posibles horas o formato ISO
    # Ejemplo: "2026-04-29T14:30" → "2026-04-29"
    fecha_texto = fecha_texto.replace("T", " ").split(" ")[0]

    # 📋 Lista de formatos que queremos aceptar
    formatos_a_probar = [
        "%d/%m/%Y",  # 29/04/2026
        "%d-%m-%Y",  # 29-04-2026
        "%Y-%m-%d"   # 2026-04-29
    ]

    # 🔁 Probamos cada formato
    for formato in formatos_a_probar:
        try:
            # Intentamos convertir la fecha
            datetime.datetime.strptime(fecha_texto, formato)

            # ✔ Si no falla, la fecha es válida
            return True

        except ValueError:
            # ❌ Si falla, probamos el siguiente formato
            continue

    # ❌ Si ninguno funciona → no es válida
    return False

def parse_fecha(fecha_texto):
    """
    Convierte una fecha en distintos formatos a datetime.
    Devuelve un datetime o None si no es válida.
    """

    if not fecha_texto:
        return None

    fecha_texto = str(fecha_texto)

    # Limpiamos formato ISO con hora (ej: 2026-04-29T14:30)
    fecha_texto = fecha_texto.replace("T", " ").split(" ")[0]

    formatos_a_probar = [
        "%d/%m/%Y",  # 29/04/2026
        "%d-%m-%Y",  # 29-04-2026
        "%Y-%m-%d"   # 2026-04-29
    ]

# Intentamos convertir y devolvemos el datetime directamente
    for formato in formatos_a_probar:
        try:
            return datetime.datetime.strptime(fecha_texto, formato)
        except ValueError:
            continue

    return None