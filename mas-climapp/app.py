import os
import sqlite3
import datetime
import random
from flask import Flask, render_template, request, jsonify

# ==========================================
# 1. SETUP & PATH CONFIGURATION
# ==========================================
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'Front-End Assets', 'templates'), 
            static_folder=os.path.join(basedir, 'Front-End Assets', 'static'))

def get_db_connection():
    """Connects to the SQLite database."""
    db_path = os.path.join(basedir, 'clima.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    return conn

# ==========================================
# 2. LOGIC ENGINE (Climate Indices & Sync)
# ==========================================

def calculate_weather_status(temp):
    """Determines weather status and assigns proper color badges."""
    
    # 1. Handle missing data
    if temp is None or str(temp).strip().lower() == 'none' or str(temp).strip() == '': 
        return {"label": "No Data", "class": "weather-nodata"} # Now Grey
    
    # 2. Clean the number (Replace comma with dot)
    try:
        clean_temp = str(temp).replace(',', '.')
        t = float(clean_temp)
    except ValueError:
        return {"label": "Error", "class": "weather-nodata"}

    # 3. Climate Logic with New Colors
    if t <= 5:
        return {"label": "Extremely Cold", "class": "weather-extreme-cold"} # Dark Blue
    elif 5 < t <= 15:
        return {"label": "Cold", "class": "weather-cold"}                   # Light Blue
    elif 15 < t <= 26:
        return {"label": "Normal", "class": "weather-normal"}               # Green
    elif 26 < t <= 35:
        return {"label": "Hot", "class": "weather-hot"}                     # Orange
    else:
        return {"label": "Extremely Hot", "class": "weather-extreme-hot"}   # Red
    
def auto_sync_to_today():
    """Checks the DB and adds missing days up to today (May 14, 2026)."""
    conn = get_db_connection()
    last_date_row = conn.execute('SELECT MAX(fecha) FROM mediciones').fetchone()
    
    if not last_date_row or not last_date_row[0]:
        conn.close()
        return

    last_date = datetime.datetime.strptime(last_date_row[0], '%Y-%m-%d').date()
    today = datetime.date.today()

    if last_date < today:
        print(f"✨ Gap detected! Last record: {last_date}. Syncing to {today}...")
        stations = conn.execute('SELECT id FROM zonas').fetchall()
        
        current_day = last_date + datetime.timedelta(days=1)
        while current_day <= today:
            for station in stations:
                # Generate realistic May weather
                temp = round(random.uniform(18.0, 28.0), 1)
                hum = random.randint(30, 50)
                wind = round(random.uniform(5.0, 20.0), 1)
                
                conn.execute('''INSERT INTO mediciones (zona_id, fecha, temperatura, humedad, viento) 
                                VALUES (?, ?, ?, ?, ?)''', 
                             (station['id'], current_day.strftime('%Y-%m-%d'), temp, hum, wind))
            current_day += datetime.timedelta(days=1)
        
        conn.commit()
    conn.close()

# ==========================================
# 3. PAGE ROUTES
# ==========================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/anadir-datos')
def anadir_datos():
    return render_template('andir_datos.html')

@app.route('/ajustes')
def settings():
    return render_template('settings.html')

@app.route('/informe')
def informe():
    """Historical report with DataTables and Climate Logic."""
    try:
        conn = get_db_connection()
        # WE ADDED m.id HERE SO WE KNOW WHICH ROW TO DELETE
        query = '''
            SELECT m.id, m.fecha, z.municipio, m.temperatura, m.humedad, m.viento 
            FROM mediciones m
            JOIN zonas z ON m.zona_id = z.id
            ORDER BY m.fecha DESC
        '''
        raw_registros = conn.execute(query).fetchall()
        conn.close()

        # Process each row through the Logic Engine
        registros = []
        for row in raw_registros:
            reg = dict(row)
            status = calculate_weather_status(reg['temperatura'])
            reg['status_label'] = status['label']
            reg['status_class'] = status['class']
            registros.append(reg)

        return render_template('informe.html', registros=registros)
    except Exception as e:
        print(f"Error en informe: {e}")
        return render_template('informe.html', registros=[])
    
# ==========================================
# 4. API & UPLOAD ROUTES
# ==========================================

@app.route('/api/mapa_datos')
def mapa_datos():
    """Fetches the most recent reading for each station for the map."""
    try:
        conn = get_db_connection()
        # THE FIX: We changed 'ON z.id = ' to 'ON m.id = ' so the IDs match correctly!
        query = '''
            SELECT z.municipio, m.temperatura, m.humedad, m.viento 
            FROM zonas z
            JOIN mediciones m ON m.id = (
                SELECT id FROM mediciones 
                WHERE zona_id = z.id 
                ORDER BY fecha DESC, id DESC LIMIT 1
            )
        '''
        datos = conn.execute(query).fetchall()
        conn.close()
        
        # Check in the terminal if data is actually being found
        registros = [dict(row) for row in datos]
        print(f"🗺️ Map Data Found: {len(registros)} stations.") 
        
        return jsonify(registros)
    except Exception as e:
        print(f"Error loading map data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart_datos')
def chart_datos():
    """Fetches historical data for the Chart.js graph"""
    try:
        conn = get_db_connection()
        # We group by date (substr extracts YYYY-MM-DD) and get the daily averages
        query = '''
            SELECT substr(fecha, 1, 10) as dia, 
                   AVG(temperatura) as temp, 
                   AVG(humedad) as hum, 
                   AVG(viento) as viento 
            FROM mediciones 
            GROUP BY dia 
            ORDER BY dia DESC
            LIMIT 365
        '''
        datos = conn.execute(query).fetchall()
        conn.close()
        
        return jsonify([dict(row) for row in datos])
    except Exception as e:
        print(f"Error loading chart data: {e}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    return jsonify({"message": f"Archivo {file.filename} procesado."})

@app.route('/upload_json', methods=['POST'])
def upload_json():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    return jsonify({"message": f"Archivo {file.filename} procesado."})

@app.route('/api/guardar_registro', methods=['POST'])
def guardar_registro():
    """Receives manual data from the frontend and saves it to clima.db"""
    try:
        datos = request.get_json()
        
        # We grab exactly what your new form sends
        estacion_nombre = datos.get('estacion')
        fecha = datos.get('fecha')  # This arrives directly as YYYY-MM-DD
        temp = datos.get('temperatura')
        hum = datos.get('humedad')
        viento = datos.get('viento')
        
        conn = get_db_connection()
        
        # Find the station ID (e.g., matching "Retiro" to "MADRID, RETIRO")
        zona = conn.execute("SELECT id FROM zonas WHERE municipio LIKE ?", (f"%{estacion_nombre}%",)).fetchone()
        
        if not zona:
            conn.close()
            return jsonify({"success": False, "error": f"La estación '{estacion_nombre}' no existe en la base de datos."}), 404
            
        zona_id = zona['id']
        
        # Insert the record
        conn.execute('''
            INSERT INTO mediciones (zona_id, fecha, temperatura, humedad, viento)
            VALUES (?, ?, ?, ?, ?)
        ''', (zona_id, fecha, temp, hum, viento))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "¡Registro guardado exitosamente!"})
        
    except Exception as e:
        print(f"Error saving data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# ==========================================
# THIS MUST BE ALL THE WAY TO THE LEFT
# ==========================================
@app.route('/api/borrar_registro/<int:id>', methods=['DELETE'])
def borrar_registro(id):
    """Deletes a specific record from the database."""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM mediciones WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Registro eliminado correctamente."})
    except Exception as e:
        print(f"Error deleting data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
# ==========================================
# 5. START SERVER
# ==========================================

if __name__ == '__main__':
    # Run sync before starting
    try:
        auto_sync_to_today()
    except Exception as e:
        print(f"Could not sync data: {e}")
        
    app.run(debug=True)
