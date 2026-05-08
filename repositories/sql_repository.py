from sqlalchemy.orm import Session
from db import crud

class SQLiteRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def save_measurement(self, measurement_data):
        return crud.create_measurement(self.db, measurement_data)
    
    def get_all_measurements(self):     
        return crud.get_measurements(self.db)
    
    