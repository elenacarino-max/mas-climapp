from flask import Blueprint, request, jsonify
from models.registro_climatico import RegistroClimatico
from utils.validators import validate_weather_data
from repositories.json_repository import JSONRepository
import json

manual_bp = Blueprint('manual', __name__)

# Instanciamos el repositorio apuntando al JSON de datos
repo = JSONRepository('data/registros_climaticos.json')

def obtener_nombre_municipio_seguro(estacion_id):
    """
    Función de respaldo: Si por algún motivo el municipio no llega del JS,
    lo rescatamos del JSON de estaciones usando el ID.
    """
    try:
        with open('static/js/estacion_por_municipio.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
            for item in datos.get("estacion_por_municipio", []):
                if item["id_estacion"] == estacion_id:
                    return item["municipio"]
    except Exception:
        pass
    return "Desconocido"

@manual_bp.route('/api/registrar', methods=['POST'])
def registrar_datos_manuales():
    """
    Controlador adaptado por Persona 4:
    - Ahora captura municipio y fuente 'manual'.
    - Limpia los datos para que Persona 4 pueda filtrar sin errores.
    """
    datos_recibidos = request.get_json()

    if not datos_recibidos:
        return jsonify({"error": "No se recibió el paquete de datos"}), 400

    # 1. CAPTURA DE IDENTIDAD (Evitamos el municipio 'null')
    estacion = datos_recibidos.get("estacion_id")
    municipio = datos_recibidos.get("municipio")
    
    if not municipio or municipio == "null":
        municipio = obtener_nombre_municipio_seguro(estacion)

    # 2. DATOS PARA VALIDAR (La fecha ya debería venir como DD/MM/AAAA desde app.js)
    datos_para_validar = {
        "fecha":         datos_recibidos.get("fecha"),
        "temperatura":   datos_recibidos.get("temperatura"),
        "humedad":       datos_recibidos.get("humedad"),
        "viento":         datos_recibidos.get("viento"),
        "lluvia":         datos_recibidos.get("lluvia")
    }
    
    print(f"\n--- REGISTRO MANUAL: {municipio} ({estacion}) ---")

    if validate_weather_data(datos_para_validar):
        try:
            # Creamos la instancia del modelo (Persona 2)
            nuevo_registro = RegistroClimatico(
                estacion, 
                datos_para_validar["fecha"], 
                float(datos_para_validar["temperatura"]), 
                float(datos_para_validar["humedad"]), 
                float(datos_para_validar["viento"]), 
                float(datos_para_validar["lluvia"])
            )
            
            # 3. CONSTRUCCIÓN DEL DICCIONARIO FINAL PARA EL JSON
            # Inyectamos los campos necesarios para que Persona 4 pueda filtrar
            datos_a_guardar = nuevo_registro.to_dict()
            datos_a_guardar["municipio"] = municipio
            datos_a_guardar["fuente"] = "manual" 

            # 4. GUARDADO
            exito_guardado = repo.guardar(datos_a_guardar)
            
            if exito_guardado:
                print(f"✔ Guardado con éxito: {municipio} el {datos_para_validar['fecha']}")
                return jsonify({
                    "status": "success",
                    "message": "✔ Registro guardado correctamente",
                    "data": datos_a_guardar
                }), 201
            else:
                return jsonify({"error": "Error al escribir en el JSON"}), 500
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return jsonify({"error": str(e)}), 400
    else:
        print("❌ FALLO DE VALIDACIÓN: Revisa el formato de fecha (DD/MM/AAAA)")
        return jsonify({
            "status": "error", 
            "message": "❌ Datos no válidos. Asegúrate de usar el formato de fecha correcto."
        }), 400