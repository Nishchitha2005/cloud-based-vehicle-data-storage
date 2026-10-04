from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from backend.app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id"),
        nullable=False,
        index=True
    )

    telemetry_id = Column(
        Integer,
        ForeignKey("telemetry.id"),
        nullable=False,
        index=True
    )

    alert_type = Column(
        String,
        nullable=False
    )

    severity = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        index=True
    )