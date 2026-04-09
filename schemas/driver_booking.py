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
class DriverBookingUpdate(BaseModel):
    user_id: Optional[int]
    driver_id: Optional[int]
    pickup_location: Optional[str]
    drop_location: Optional[str]
    booking_date: Optional[str]
    booking_time: Optional[str]
    duration_hours: Optional[int]
    contact_number: Optional[str]
    status: Optional[str]

    class Config:
        orm_mode = True 

# RESPONSE
class DriverBookingOut(DriverBookingCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
