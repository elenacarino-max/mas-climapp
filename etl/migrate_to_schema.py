import sqlite3
import os
from datetime import datetime

# Conexión manual (sin SQLAlchemy/Pandas)
DB_PATH = 'etl/clima.db'

def migrar_a_esquema_nuevo():
    if not os.path.exists(DB_PATH):
        print("Error: No se encuentra la base de datos.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Crear las tablas con el esquema solicitado
    print("Creando tablas según el esquema...")
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS zonas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        municipio TEXT NOT NULL,
        cod_ine TEXT UNIQUE NOT NULL,
        id_estacion TEXT NOT NULL,
        estacion_referencia TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS mediciones_final (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        zona_id INTEGER NOT NULL,
        fecha_datos TEXT NOT NULL,
        temperatura REAL,
        humedad REAL,
        viento REAL,
        lluvia REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (zona_id) REFERENCES zonas(id),
        UNIQUE(fecha_datos, zona_id)
    );
    """)

    # 2. Insertar las zonas iniciales
    estaciones_info = [
        ("Madrid", "2807901", "3195", "Madrid, Retiro"),
        ("Madrid", "2807902", "3129", "Madrid, Aeropuerto Barajas"),
        ("Madrid", "2807903", "3194U", "Madrid, Cuatro Vientos"),
        ("Madrid", "2807904", "3196", "Madrid, Ciudad Universitaria"),
        ("Getafe", "2806501", "3200", "Getafe")
    ]

    for info in estaciones_info:
        cursor.execute("""
            INSERT OR IGNORE INTO zonas (municipio, cod_ine, id_estacion, estacion_referencia)
            VALUES (?, ?, ?, ?)
        """, info)

    # 3. Mapear y migrar datos de clima_master a mediciones_final
    print("Migrando registros desde clima_master...")
    
    # Obtenemos el mapa de {id_estacion: zona_id}
    cursor.execute("SELECT id_estacion, id FROM zonas")
    zona_map = dict(cursor.fetchall())

    # Seleccionamos los datos del master
    cursor.execute("SELECT estacion_id, fecha, temp_media, precipitacion FROM clima_master")
    filas = cursor.fetchall()

    cont = 0
    for estacion_id, fecha, temp, prec in filas:
        z_id = zona_map.get(str(estacion_id))
        if z_id:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO mediciones_final 
                    (zona_id, fecha_datos, temperatura, lluvia)
                    VALUES (?, ?, ?, ?)
                """, (z_id, fecha, temp, prec))
                cont += 1
            except Exception:
                continue

    conn.commit()
    conn.close()
    print(f"¡Éxito! Se han migrado {cont} registros al nuevo esquema.")

if __name__ == "__main__":
    migrar_a_esquema_nuevo()