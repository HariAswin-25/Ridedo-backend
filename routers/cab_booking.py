from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.cab_booking import CabBooking
from models.user import User   
from schemas.cab_booking import (
    CabBookingCreate,
    CabBookingUpdate,
    CabBookingOut
)

router = APIRouter(prefix="/cab-bookings", tags=["Cab Bookings"])


# READ UNASSIGNED (For Drivers)
@router.get("/unassigned", response_model=list[CabBookingOut])
def get_unassigned_bookings(db: Session = Depends(get_db)):
    return db.query(CabBooking).filter(CabBooking.driver_id == None).all()


# ACCEPT BOOKING (For Drivers)
@router.put("/{booking_id}/accept", response_model=CabBookingOut)
def accept_booking(booking_id: int, driver_id: int, db: Session = Depends(get_db)):
    booking = db.query(CabBooking).filter(CabBooking.id == booking_id).first()
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
@router.post("/create", response_model=CabBookingOut)
def create_booking(data: CabBookingCreate, db: Session = Depends(get_db)):

    #  CHECK USER EXISTS
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please create user first."
        )

    booking = CabBooking(**data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


# READ ONE
@router.get("/{booking_id}", response_model=CabBookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(CabBooking).filter(CabBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


# READ ALL
@router.get("/", response_model=list[CabBookingOut])
def get_all_bookings(db: Session = Depends(get_db)):
    return db.query(CabBooking).all()


# UPDATE
@router.put("/{booking_id}", response_model=CabBookingOut)
def update_booking(
    booking_id: int,
    data: CabBookingUpdate,
    db: Session = Depends(get_db)
):
    booking = db.query(CabBooking).filter(CabBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(booking, key, value)

    # If status updated, sync Driver status
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
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(CabBooking).filter(CabBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.driver_id:
        from models.driver import Driver
        driver = db.query(Driver).filter(Driver.id == booking.driver_id).first()
        if driver:
            driver.status = "available"

    db.delete(booking)
    db.commit()
    return {"message": "Booking cancelled successfully"}
