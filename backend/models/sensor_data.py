from app import db

class SensorData(db.Model):
    __tablename__ = 'sensor_data'

    device_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), primary_key=True)
    temperature = db.Column(db.Numeric(5, 2))
    humidity = db.Column(db.Numeric(5, 2))
    pollen = db.Column(db.Integer)
    particulate_matter = db.Column(db.Integer)
