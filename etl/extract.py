import pandas as pd
import json
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

def obtener_sesion_con_reintentos():
    """Configures a resilient connection with 3 retries and exponential backoff."""
    session = requests.Session()
    reintentos = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adaptador = HTTPAdapter(max_retries=reintentos)
    session.mount("https://", adaptador)
    session.mount("http://", adaptador)
    return session

def extraer_desde_api():
    if not API_KEY:
        print("Error: No se encontró la API_KEY en el archivo .env")
        return None
        
    print("Paso 1: Solicitando acceso a AEMET...")
    url_aemet = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
    sesion = obtener_sesion_con_reintentos()
    
    try:
        # Usar la sesión con reintentos en lugar de requests.get normal
        respuesta = sesion.get(url_aemet, params={"api_key": API_KEY}, timeout=10)
        respuesta.raise_for_status() 
        
        respuesta_json = respuesta.json()
        
        if respuesta_json.get("estado") == 200:
            enlace_datos = respuesta_json.get("datos")
            print("Paso 2: Acceso concedido. Descargando los datos reales...")
            
            # Usar la sesión con reintentos aquí también
            respuesta_datos = sesion.get(enlace_datos, timeout=15)
            
            try:
                datos_climaticos = respuesta_datos.json()
            except ValueError:
                print("\nError: AEMET no envió un JSON válido.")
                return None
            
            df = pd.DataFrame(datos_climaticos)
            ruta_estaciones = "../config/estaciones_madrid.json"
            
            try:
                with open(ruta_estaciones, 'r', encoding='utf-8') as f:
                    estaciones_madrid = json.load(f)
                idema_madrid = [estacion['idema'] for estacion in estaciones_madrid]
                df_madrid = df[df['idema'].isin(idema_madrid)]
                return df_madrid
            except FileNotFoundError:
                return df
                
        else:
            print(f"Error de AEMET: {respuesta_json.get('descripcion')}")
            return None
            
    except Exception as e:
        print(f"Ocurrió un error (incluso después de los reintentos): {e}")
        return None

if __name__ == "__main__":
    df_api = extraer_desde_api()
    
    if df_api is not None:
        print("\n--- Primeros 3 registros de AEMET (Madrid) ---")
        columnas_interes = ['idema', 'ubi', 'fint', 'ta', 'tamax', 'tamin']
        columnas_disponibles = [col for col in columnas_interes if col in df_api.columns]
        print(df_api[columnas_disponibles].head(3))