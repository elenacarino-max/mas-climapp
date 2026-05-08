from sqlalchemy.orm import Session
from . import models

def get_measurements(db: Session):
    return db.query(models.Measurement).all()

def create_measurement(db: Session, measurement_data):
    db_measurement = models.Measurement(**measurement_data)
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement
