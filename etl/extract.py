import pandas as pd
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def extraer_desde_api():
    if not API_KEY:
        print("Error: No se encontró la API_KEY en el archivo .env")
        return None
        
    print("Paso 1: Solicitando acceso a AEMET...")
    url_aemet = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
    
    try:
        respuesta = requests.get(url_aemet, params={"api_key": API_KEY})
        respuesta.raise_for_status() 
        
        respuesta_json = respuesta.json()
        
        if respuesta_json.get("estado") == 200:
            enlace_datos = respuesta_json.get("datos")
            print("Paso 2: Acceso concedido. Descargando los datos reales...")
            
            # --- THE NEW SAFETY NET ---
            # We add a timeout so it doesn't hang forever, and we verify the SSL
            respuesta_datos = requests.get(enlace_datos, timeout=10)
            
            # Check if AEMET sent a successful HTTP code (200)
            if respuesta_datos.status_code != 200:
                print(f"Error: AEMET falló en el Paso 2 con código HTTP {respuesta_datos.status_code}.")
                return None
                
            try:
                # Attempt to parse the JSON
                datos_climaticos = respuesta_datos.json()
            except ValueError:
                # If it's not JSON (this is the Expecting value error!), print what it actually is
                print("\nError: AEMET no envió un JSON válido. Esto es lo que envió en su lugar:\n")
                print(respuesta_datos.text[:500]) # Print the first 500 characters
                return None
            
            # Convert to Pandas DataFrame
            df = pd.DataFrame(datos_climaticos)
            print(f"Descargados {len(df)} registros totales de España.")
            
            ruta_estaciones = "../config/estaciones_madrid.json"
            
            try:
                with open(ruta_estaciones, 'r', encoding='utf-8') as f:
                    estaciones_madrid = json.load(f)
                
                idema_madrid = [estacion['idema'] for estacion in estaciones_madrid]
                df_madrid = df[df['idema'].isin(idema_madrid)]
                
                print(f"Filtrado completado. Se encontraron {len(df_madrid)} registros de Madrid.")
                return df_madrid
                
            except FileNotFoundError:
                print(f"Aviso: No se encontró {ruta_estaciones}. Devolviendo todos los datos.")
                return df
                
        else:
            print(f"Error de AEMET: {respuesta_json.get('descripcion')}")
            return None
            
    except Exception as e:
        print(f"Ocurrió un error al consultar la API: {e}")
        return None

if __name__ == "__main__":
    df_api = extraer_desde_api()
    
    if df_api is not None:
        print("\n--- Primeros 3 registros de AEMET (Madrid) ---")
        columnas_interes = ['idema', 'ubi', 'fint', 'ta', 'tamax', 'tamin']
        columnas_disponibles = [col for col in columnas_interes if col in df_api.columns]
        print(df_api[columnas_disponibles].head(3))