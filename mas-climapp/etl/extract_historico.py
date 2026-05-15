import pandas as pd
import json
import os
import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def obtener_sesion_con_reintentos():
    session = requests.Session()
    reintentos = Retry(
        total=5,
        backoff_factor=2, 
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adaptador = HTTPAdapter(max_retries=reintentos)
    session.mount("https://", adaptador)
    session.mount("http://", adaptador)
    return session

def extraer_rango_historico(anio_inicio=2024, anio_fin=2026):
    if not API_KEY:
        print("Error: No se encontró la API_KEY")
        return None

    ruta_estaciones = "../config/estaciones_madrid.json"
    try:
        with open(ruta_estaciones, 'r', encoding='utf-8') as f:
            estaciones_madrid = json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró {ruta_estaciones}")
        return None

    sesion = obtener_sesion_con_reintentos()
    headers = {"api_key": API_KEY}
    todos_los_datos = []

    # Lista de meses (inicio, fin)
    meses = [
        ("01-01", "01-31"), ("02-01", "02-28"), ("03-01", "03-31"),
        ("04-01", "04-30"), ("05-01", "05-31"), ("06-01", "06-30"),
        ("07-01", "07-31"), ("08-01", "08-31"), ("09-01", "09-30"),
        ("10-01", "10-31"), ("11-01", "11-30"), ("12-01", "12-31")
    ]

    # LOOP 1: Por cada año en el rango
    for anio in range(anio_inicio, anio_fin + 1):
        print(f"\n>>>> PROCESANDO AÑO: {anio} <<<<")
        
        # LOOP 2: Por cada estación
        for estacion in estaciones_madrid:
            idema = estacion['idema']
            nombre = estacion['nombre']
            print(f"\nEstación: {nombre} ({idema})")

            # LOOP 3: Por cada mes (El "Chunk")
            for inicio, fin in meses:
                # Evitar pedir fechas del futuro si hoy es 2026
                # (AEMET da error 404 si pides meses que aún no han pasado)
                fecha_ini = f"{anio}-{inicio}T00:00:00UTC"
                fecha_fin = f"{anio}-{fin}T23:59:59UTC"
                
                url_aemet = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fecha_ini}/fechafin/{fecha_fin}/estacion/{idema}"
                
                try:
                    respuesta = sesion.get(url_aemet, headers=headers, timeout=20)
                    # Si recibimos un 404, probablemente es porque el mes aún no ha ocurrido
                    if respuesta.status_code == 404:
                        continue 
                        
                    res_json = respuesta.json()
                    if res_json.get("estado") == 200:
                        enlace_datos = res_json.get("datos")
                        datos_raw = sesion.get(enlace_datos, timeout=20).json()
                        todos_los_datos.extend(datos_raw)
                        print(f"  -> {anio}-{inicio}: {len(datos_raw)} registros OK.")
                    
                    time.sleep(1.2) # Respetar el límite de la API

                except Exception as e:
                    print(f"  -> Error en {anio}-{inicio}: {e}")

    if not todos_los_datos:
        return None
        
    df_final = pd.DataFrame(todos_los_datos)
    print(f"\n=== PROCESO FINALIZADO ===")
    print(f"Total de registros acumulados: {len(df_final)}")
    return df_final

if __name__ == "__main__":
    # Ejecutamos para el rango 2024 - 2026
    df_total = extraer_rango_historico(2024, 2026)
    
    if df_total is not None:
        df_total.to_csv("datos_madrid_2024_2026.csv", index=False)
        print("Archivo 'datos_madrid_2024_2026.csv' creado exitosamente.")