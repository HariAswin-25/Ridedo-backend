from pydantic import BaseModel
from typing import List
from schemas.cab_booking import CabBookingOut
from schemas.vehicle_rental import VehicleRentalOut
from schemas.driver_booking import DriverBookingOut

class UserActivity(BaseModel):
    cab_bookings: List[CabBookingOut]
    vehicle_rentals: List[VehicleRentalOut]
    driver_bookings: List[DriverBookingOut]

    class Config:
        from_attributes = True
