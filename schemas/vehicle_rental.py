from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional


class VehicleRentalBase(BaseModel):
    user_id: int
    vehicle_id: Optional[int] = None
    pickup_location: str
    phone_number: str
    driving_license_number: str
    pickup_date: date
    pickup_time: time
    return_date: date
    return_time: time


class VehicleRentalCreate(VehicleRentalBase):
    pass


class VehicleRentalUpdate(BaseModel):
    pickup_location: Optional[str] = None
    phone_number: Optional[str] = None
    driving_license_number: Optional[str] = None
    pickup_date: Optional[date] = None
    pickup_time: Optional[time] = None
    return_date: Optional[date] = None
    return_time: Optional[time] = None
    status: Optional[str] = None


class VehicleRentalOut(VehicleRentalBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
