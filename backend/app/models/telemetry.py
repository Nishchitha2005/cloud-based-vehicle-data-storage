from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.app.database import Base


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    timestamp = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True
    )

    speed = Column(Float, nullable=False)
    engine_rpm = Column(Float, nullable=False)
    engine_temperature = Column(Float, nullable=False)
    fuel_level = Column(Float, nullable=False)
    battery_voltage = Column(Float, nullable=False)

    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)