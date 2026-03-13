from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.driver_booking import DriverBooking
from schemas.driver_booking import (
    DriverBookingCreate,
    DriverBookingUpdate,
    DriverBookingOut
)

router = APIRouter(
    prefix="/driver-bookings",
    tags=["Driver Bookings"]
)

# READ UNASSIGNED (For Drivers)
@router.get("/unassigned", response_model=list[DriverBookingOut])
def get_unassigned_driver_bookings(db: Session = Depends(get_db)):
    return db.query(DriverBooking).filter(DriverBooking.driver_id == None).all()


# ACCEPT BOOKING (For Drivers)
@router.put("/{booking_id}/accept", response_model=DriverBookingOut)
def accept_driver_booking(booking_id: int, driver_id: int, db: Session = Depends(get_db)):
    booking = db.query(DriverBooking).filter(DriverBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.driver_id is not None:
        raise HTTPException(status_code=400, detail="Booking already accepted by another driver")

    booking.driver_id = driver_id
    booking.status = "Accepted"
    
    # Sync Driver status
    from models.driver import Driver
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if driver:
        driver.status = "unavailable"

    db.commit()
    db.refresh(booking)
    return booking

# CREATE
@router.post("/create", response_model=DriverBookingOut)
def create_driver_booking(
    data: DriverBookingCreate,
    db: Session = Depends(get_db)
):
    booking = DriverBooking(**data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


# GET ONE
@router.get("/{booking_id}", response_model=DriverBookingOut)
def get_driver_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(DriverBooking).filter(
        DriverBooking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Driver booking not found")

    return booking


# GET ALL
@router.get("/", response_model=list[DriverBookingOut])
def get_all_driver_bookings(
    db: Session = Depends(get_db)
):
    return db.query(DriverBooking).all()


# UPDATE
@router.put("/{booking_id}", response_model=DriverBookingOut)
def update_driver_booking(
    booking_id: int,
    data: DriverBookingUpdate,
    db: Session = Depends(get_db)
):
    booking = db.query(DriverBooking).filter(
        DriverBooking.id == booking_id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Driver booking not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(booking, key, value)

    # If status is updated, sync Driver status
    if data.status:
        from models.driver import Driver
        driver = db.query(Driver).filter(Driver.id == booking.driver_id).first()
        if driver:
            status_lower = data.status.lower()
            if status_lower in ["finished", "cancelled", "completed", "rejected"]:
                driver.status = "available"
            elif status_lower in ["accepted", "confirmed"]:
                driver.status = "unavailable"

    db.commit()
    db.refresh(booking)
    return booking


# DELETE
@router.delete("/{booking_id}")
def cancel_driver_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(DriverBooking).filter(DriverBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Driver booking not found")

    if booking.driver_id:
        from models.driver import Driver
        driver = db.query(Driver).filter(Driver.id == booking.driver_id).first()
        if driver:
            driver.status = "available"

    db.delete(booking)
    db.commit()
    return {"message": "Driver booking cancelled successfully"}
