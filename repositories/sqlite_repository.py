from sqlalchemy.orm import Session
from db import crud

class SQLiteRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_zone(self, zone_data: dict):
        """
        Busca la zona por código INE. Si no existe, la crea.
        """
        db_zona = crud.obtener_zona_por_codigo(self.db, cod_ine=zone_data['cod_ine'])
        
        if not db_zona:
            db_zona = crud.crear_zona(
                db=self.db,
                municipio=zone_data['municipio'],
                cod_ine=zone_data['cod_ine'],
                id_estacion=zone_data['id_estacion'],
                estacion_referencia=zone_data['estacion_referencia']
            )
        return db_zona

    def save_measurement(self, measurement_data: dict, zona_id: int):
        """
        Guarda una medición asociada a una zona.
        """
        return crud.crear_medicion(
            db=self.db,
            medicion_data=measurement_data,
            zona_id=zona_id
        )