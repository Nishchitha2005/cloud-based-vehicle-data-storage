from sqlalchemy import Column, Integer, String

from backend.app.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String, unique=True, nullable=False, index=True)
    vin = Column(String, unique=True, nullable=False)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    year = Column(Integer, nullable=False)