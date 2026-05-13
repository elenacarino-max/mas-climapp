import pandas as pd
from sqlalchemy import create_engine
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def cargar_datos(df_limpio, nombre_tabla="mediciones"):
    if not DATABASE_URL:
        logger.error("No se encontró DATABASE_URL en el archivo .env")
        return False

    if df_limpio is None or df_limpio.empty:
        logger.warning("No hay datos limpios para cargar en la base de datos.")
        return False

    logger.info(f"Conectando a la base de datos para insertar datos en la tabla '{nombre_tabla}'...")
    
    try:
        engine = create_engine(DATABASE_URL)
        df_limpio.to_sql(nombre_tabla, con=engine, if_exists='append', index=False)
        logger.info(f"¡Éxito! Se han guardado {len(df_limpio)} registros en la base de datos.")
        return True
        
    except Exception as e:
        logger.error(f"Fallo crítico al guardar en la base de datos: {e}")
        return False

if __name__ == "__main__":
    print("Este archivo contiene la lógica de carga. Ejecuta etl_runner.py para probar el proceso completo.")