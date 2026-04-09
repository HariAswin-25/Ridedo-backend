from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime

# Base
class CabBookingBase(BaseModel):
    user_id: int
    pickup_location: str
    destination: str
    cab_type: str
    booking_date: date
    booking_time: time


# CREATE
class CabBookingCreate(CabBookingBase):
    pass

# RESPONSE
class CabBookingOut(CabBookingBase):
    id: int
    driver_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
