import json
import os
from pathlib import Path
from typing import Optional

from services.logging_service import log_info, log_warning, log_error


DATA_FILE = Path("data/registros_climaticos.json")


def load_all() -> list:
    if not DATA_FILE.exists():
        log_warning("El archivo de registros no existe todavía. Se devuelve una lista vacía.")
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        log_error("El contenido del archivo JSON no es una lista válida.")
        return []

    except json.JSONDecodeError:
        log_error("Error al leer el archivo JSON: formato inválido o archivo corrupto.")
        return []

    except OSError as error:
        log_error(f"Error del sistema al intentar leer el archivo JSON: {error}")
        return []


def save_all(records: list) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=4)

        log_info("Registros guardados correctamente en el archivo JSON.")

    except OSError as error:
        log_error(f"Error al guardar registros en el archivo JSON: {error}")


def record_exists(record_id: str, records: list) -> bool:
    return any(record.get("id") == record_id for record in records)


def append(record: dict) -> dict:
    records = load_all()
    record_id = record.get("id")

    if not record_id:
        log_error("Se intentó guardar un registro sin campo 'id'.")
        return {
            "success": False,
            "message": "El registro no tiene campo 'id'."
        }

    if record_exists(record_id, records):
        log_warning(f"Registro duplicado detectado: {record_id}")
        return {
            "success": False,
            "message": f"El registro con id '{record_id}' ya existe."
        }

    records.append(record)
    save_all(records)

    log_info(f"Registro guardado correctamente: {record_id}")

    return {
        "success": True,
        "message": "Registro guardado correctamente.",
        "record_id": record_id
    }


def find_latest_by_municipio_and_source(municipio: str, fuente: str) -> Optional[dict]:
    records = load_all()

    filtered = [
        record for record in records
        if record.get("municipio") == municipio and record.get("fuente") == fuente
    ]

    if not filtered:
        log_warning(f"No se encontraron registros para municipio='{municipio}' y fuente='{fuente}'.")
        return None

    filtered.sort(key=lambda record: record.get("fecha", ""), reverse=True)

    latest_record = filtered[0]

    log_info(
        f"Último registro encontrado para municipio='{municipio}' y fuente='{fuente}': "
        f"{latest_record.get('id', 'sin_id')}"
    )

    return latest_record


def filter_records(municipio: Optional[str] = None, fecha: Optional[str] = None) -> list:
    records = load_all()

    if municipio:
        records = [
            record for record in records
            if record.get("municipio") == municipio
        ]

    if fecha:
        records = [
            record for record in records
            if record.get("fecha", "").startswith(fecha)
        ]

    log_info(
        f"Filtro aplicado sobre registros. "
        f"municipio='{municipio}', fecha='{fecha}', resultados={len(records)}"
    )

    return records


class JSONRepository:
    """
    Clase mantenida desde main para no romper otras partes del proyecto
    que puedan estar usando JSONRepository(file_path).guardar(...).
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def guardar(self, registro_dict):
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as file:
                    try:
                        datos = json.load(file)
                    except json.JSONDecodeError:
                        datos = []
            else:
                datos = []

            datos.append(registro_dict)

            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(datos, file, indent=4, ensure_ascii=False)

            log_info(f"Registro guardado mediante JSONRepository en {self.file_path}")
            return True

        except Exception as error:
            log_error(f"Error crítico en JSONRepository: {error}")
            return False