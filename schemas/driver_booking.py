from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# CREATE
class DriverBookingCreate(BaseModel):
    user_id: int
    driver_id: Optional[int] = None
    pickup_location: str
    drop_location: str
    booking_date: str
    booking_time: str
    duration_hours: int
    contact_number: str


# UPDATE
class DriverBookingUpdate(BaseModel):
    pickup_location: Optional[str] = None
    drop_location: Optional[str] = None
    booking_date: Optional[str] = None
    booking_time: Optional[str] = None
    duration_hours: Optional[int] = None
    contact_number: Optional[str] = None
    status: Optional[str] = None


# RESPONSE
class DriverBookingOut(DriverBookingCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
