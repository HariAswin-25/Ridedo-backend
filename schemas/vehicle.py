from pydantic import BaseModel
from typing import Optional


# BASE
class VehicleBase(BaseModel):
    vehicle_type: str
    vehicle_name: str
    vehicle_number: str
    fuel_type: str
    rent_per_day: int
    image_url: Optional[str] = None


# CREATE
class VehicleCreate(VehicleBase):
    owner_id: Optional[int] = None # User who is listing the vehicle


# UPDATE
class VehicleUpdate(BaseModel):
    vehicle_type: Optional[str] = None
    vehicle_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    fuel_type: Optional[str] = None
    rent_per_day: Optional[int] = None
    availability: Optional[str] = None
    image_url: Optional[str] = None


# RESPONSE
class VehicleOut(VehicleBase):
    id: int
    owner_id: Optional[int] = None
    availability: str

    class Config:
        from_attributes = True
