from pydantic import BaseModel


class VehicleAnalyticsResponse(BaseModel):
    vehicle_id: int
    total_records: int
    average_speed: float
    maximum_speed: float
    average_engine_rpm: float
    maximum_engine_temperature: float
    minimum_fuel_level: float
    average_battery_voltage: float