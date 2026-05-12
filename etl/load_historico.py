import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def cargar_historico():
    # 1. Leer el CSV que acabas de generar
    file_path = "datos_madrid_2024_2026.csv"
    if not os.path.exists(file_path):
        print(f"Error: No se encuentra {file_path}")
        return

    df = pd.read_csv(file_path)

    # 2. Limpieza básica y Renombrado (Transformación rápida)
    # Convertimos las comas decimales (estilo español) a puntos (estilo Python)
    cols_numericas = ['tmed', 'prec', 'tmin', 'tmax', 'velmedia']
    for col in cols_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '.').replace('Ip', '0.0')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Renombrar columnas para que sean más claras
    df = df.rename(columns={
        'indicativo': 'estacion_id',
        'tmed': 'temp_media',
        'tmin': 'temp_min',
        'tmax': 'temp_max',
        'prec': 'precipitacion',
        'velmedia': 'viento_media'
    })

    # 3. Cargar en la Base de Datos
    engine = create_engine(DATABASE_URL)
    # Creamos una tabla nueva llamada 'historico_clima'
    df.to_sql('historico_clima', con=engine, if_exists='replace', index=False)
    
    print(f"¡Éxito! Se han cargado {len(df)} registros en la tabla 'historico_clima'.")

if __name__ == "__main__":
    cargar_historico()