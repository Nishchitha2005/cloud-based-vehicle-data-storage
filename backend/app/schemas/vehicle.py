from pydantic import BaseModel


class VehicleCreate(BaseModel):
    vehicle_id: str
    vin: str
    manufacturer: str
    model: str
    year: int


class VehicleResponse(BaseModel):
    id: int
    vehicle_id: str
    vin: str
    manufacturer: str
    model: str
    year: int

    class Config:
        from_attributes = True