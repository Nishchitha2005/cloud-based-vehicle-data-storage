from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TelemetryCreate(BaseModel):
    vehicle_id: int = Field(gt=0)

    speed: float = Field(ge=0, le=250)

    engine_rpm: float = Field(ge=0, le=8000)

    engine_temperature: float = Field(ge=-40, le=150)

    fuel_level: float = Field(ge=0, le=100)

    battery_voltage: float = Field(ge=0, le=20)

    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180
    )


class TelemetryResponse(BaseModel):
    id: int
    vehicle_id: int
    timestamp: datetime

    speed: float
    engine_rpm: float
    engine_temperature: float
    fuel_level: float
    battery_voltage: float

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    class Config:
        from_attributes = True