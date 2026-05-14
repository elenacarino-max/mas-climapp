import json
import os

class JSONRepository:
    def __init__(self, file_path=None):
        if file_path is None:
            self.file_path = os.path.join("data", "registros_climaticos.json")
        else:
            self.file_path = file_path
        
        self.stations_path = os.path.join("static", "estacion_por_municipio.json")
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def guardar(self, registro_dict):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            datos.append(registro_dict)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al escribir en el JSON: {e}")
            return False

    def filtrar_registros(self, municipio=None, fuente=None, fecha=None):
        """
        FILTRADO CORREGIDO: 
        Ahora busca directamente por el texto del municipio en el JSON.
        """
        try:
            if not os.path.exists(self.file_path):
                return []
                
            with open(self.file_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            # 1. Filtro por Municipio (Busca el nombre directamente)
            if municipio:
                # Comparamos en minúsculas para evitar fallos por tildes/mayúsculas
                datos = [r for r in datos if municipio.lower() in str(r.get('municipio', '')).lower()]
            
            # 2. Filtro por Fecha (Busca el texto exacto DD/MM/AAAA)
            if fecha:
                datos = [r for r in datos if str(r.get('fecha')) == str(fecha)]

            # 3. Filtro por Fuente (manual/aemet)
            if fuente:
                datos = [r for r in datos if r.get('fuente') == fuente]
                
            return datos
        except Exception as e:
            print(f"Error en filtrar_registros: {e}")
            return []

    def obtener_ultimo_registro(self, municipio, fuente):
        """Para la comparativa: busca el último registro de un municipio."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                for r in reversed(datos):
                    # Comprobamos que el municipio coincida
                    if r.get('municipio', '').lower() == municipio.lower():
                        return r
            return None
        except Exception:
            return None

# --- FUNCIONES DE INTERFAZ ---
_repo = JSONRepository()

def filter_records(**kwargs):
    return _repo.filtrar_registros(
        municipio=kwargs.get('municipio'),
        fuente=kwargs.get('fuente'),
        fecha=kwargs.get('fecha')
    )

def find_latest_by_municipio_and_source(municipio, fuente):
    return _repo.obtener_ultimo_registro(municipio, fuente)

def guardar_registro(registro_dict):
    return _repo.guardar(registro_dict)