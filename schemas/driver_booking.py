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


# RESPONSE
class DriverBookingOut(DriverBookingCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
