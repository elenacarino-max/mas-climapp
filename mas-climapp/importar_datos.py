import sqlite3
import pandas as pd
import os

def import_csv_to_db():
    csv_file = 'datos_madrid_2024_2026.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: File {csv_file} not found.")
        return

    # 1. Load the CSV (Detecting encoding for Spanish characters)
    try:
        df = pd.read_csv(csv_file, encoding='utf-8')
        if len(df.columns) < 2: raise ValueError
    except:
        df = pd.read_csv(csv_file, sep=';', encoding='latin-1')

    print(f"✅ CSV loaded with {len(df)} records.")

    # 2. Database Connection
    conn = sqlite3.connect('clima.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS zonas 
                      (id INTEGER PRIMARY KEY, id_estacion TEXT UNIQUE, municipio TEXT)''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS mediciones 
                      (id INTEGER PRIMARY KEY, zona_id INTEGER, fecha TEXT, 
                       temperatura REAL, humedad REAL, viento REAL,
                       FOREIGN KEY(zona_id) REFERENCES zonas(id))''')

    # 3. Insert Stations (Zonas)
    print("Synchronizing stations...")
    # Based on your CSV: 'indicativo' is the ID, 'nombre' is the Station Name
    estaciones = df[['indicativo', 'nombre']].drop_duplicates()
    for _, row in estaciones.iterrows():
        cursor.execute("INSERT OR IGNORE INTO zonas (id_estacion, municipio) VALUES (?, ?)", 
                       (str(row['indicativo']), row['nombre']))

    # 4. Insert Measurements
    print("Inserting measurements (this may take a few seconds)...")
    for _, row in df.iterrows():
        # Get the internal ID for the station
        cursor.execute("SELECT id FROM zonas WHERE id_estacion = ?", (str(row['indicativo']),))
        zona_id = cursor.fetchone()[0]
        
        # Mapping: tmed -> temp, hrMedia -> hum, velmedia -> wind
        cursor.execute('''INSERT INTO mediciones (zona_id, fecha, temperatura, humedad, viento) 
                          VALUES (?, ?, ?, ?, ?)''', 
                       (zona_id, 
                        row['fecha'], 
                        row['tmed'], 
                        row['hrMedia'], 
                        row['velmedia']))

    conn.commit()
    conn.close()
    print("✅ SUCCESS! Historical data loaded into clima.db")

if __name__ == "__main__":
    import_csv_to_db()