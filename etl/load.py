import sqlite3
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
DB_PATH = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL else "etl/clima.db"

def cargar_datos(datos_limpios, nombre_tabla="mediciones"):
    """
    Carga los datos en la base de datos usando sqlite3 nativo.
    Realiza la conversión de 'idema' (string) a 'zona_id' (integer) 
    consultando la tabla 'zonas'.
    """
    if not os.path.exists(DB_PATH):
        logger.error(f"No se encontró la base de datos en: {DB_PATH}")
        return False

    if not datos_limpios:
        logger.warning("No hay datos para cargar.")
        return False

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        logger.info("Consultando tabla 'zonas' para mapear IDs...")
        cursor.execute("SELECT id_estacion, id FROM zonas")
        mapa_zonas = {str(row[0]): row[1] for row in cursor.fetchall()}

        registros_para_insertar = []
        descartados = 0

        for fila in datos_limpios:
            estacion_aemet = str(fila.get('zona_id'))
            
            if estacion_aemet in mapa_zonas:
                id_real_db = mapa_zonas[estacion_aemet]
                
                registros_para_insertar.append((
                    id_real_db,
                    fila.get('fecha_datos'),
                    fila.get('temperatura'),
                    fila.get('lluvia'),
                    fila.get('viento'),
                    fila.get('humedad')
                ))
            else:
                descartados += 1

        if descartados > 0:
            logger.warning(f"Se descartaron {descartados} registros porque la estación no existe en la tabla 'zonas'.")

        logger.info(f"Insertando {len(registros_para_insertar)} registros en '{nombre_tabla}'...")
        query = f"""
            INSERT OR IGNORE INTO {nombre_tabla} 
            (zona_id, fecha_datos, temperatura, lluvia, viento, humedad)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.executemany(query, registros_para_insertar)
        conn.commit()
        
        filas_afectadas = cursor.rowcount
        conn.close()
        
        logger.info(f"¡Éxito! Se han guardado {len(registros_para_insertar)} registros.")
        return True

    except Exception as e:
        logger.error(f"Fallo crítico al cargar datos: {e}")
        return False

if __name__ == "__main__":
    print("Módulo de carga listo. Usa etl_runner.py para ejecutar el proceso.")