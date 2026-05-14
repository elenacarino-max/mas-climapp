import sqlite3
import os

# Path to your database
db_path = 'etl/clima.db'

def consolidar_sin_librerias():
    if not os.path.exists(db_path):
        print(f"Error: No se encuentra el archivo en {db_path}")
        return

    # Conectar directamente usando la librería nativa de Python
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Limpiando datos previos...")
    cursor.execute("DROP TABLE IF EXISTS clima_master")

    print("Mezclando tablas (Histórico + Realtime)...")
    
    # El comando SQL mágico que une todo
    # El comando SQL actualizado con los nombres de columna correctos
    sql_merge = """
    CREATE TABLE clima_master AS 
    SELECT 
        estacion_id, 
        fecha, 
        temp_media, 
        precipitacion, 
        'HISTORICO' AS fuente 
    FROM historico_clima
    UNION ALL
    SELECT 
        idema AS estacion_id, 
        fint AS fecha, 
        ta AS temp_media, 
        prec AS precipitacion, 
        'REALTIME' AS fuente 
    FROM medicion;
    """

    try:
        cursor.execute(sql_merge)
        conn.commit()
        print("--- ¡ÉXITO TOTAL! ---")
        print("La tabla 'clima_master' ha sido creada sin usar Pandas.")
    except Exception as e:
        print(f"Error en el SQL: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    consolidar_sin_librerias()