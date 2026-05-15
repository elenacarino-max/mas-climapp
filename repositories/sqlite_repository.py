from sqlalchemy.orm import Session
from db import crud

class SQLiteRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_zone(self, zone_data: dict):
        # Usamos .get() para evitar KeyError y delegamos la lógica al CRUD
        # El CRUD ya se encarga de evitar duplicados por cod_ine
        return crud.crear_zona(self.db, zone_data)

    def save_measurement(self, measurement_data: dict, zona_id: int):
        # Delegamos la creación al CRUD que ya tiene las validaciones
        return crud.medicion_crear(self.db, measurement_data, zona_id)