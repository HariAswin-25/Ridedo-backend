from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.vehicle_rental import VehicleRental
from schemas.vehicle_rental import (
    VehicleRentalCreate,
    VehicleRentalUpdate,
    VehicleRentalOut
)

router = APIRouter(prefix="/rentals", tags=["Vehicle Rentals"])


# CREATE RENTAL
@router.post("/create", response_model=VehicleRentalOut)
def create_rental(
    data: VehicleRentalCreate,
    db: Session = Depends(get_db)
):
    rental = VehicleRental(**data.dict())
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


# GET ALL RENTALS
@router.get("/", response_model=list[VehicleRentalOut])
def get_all_rentals(db: Session = Depends(get_db)):
    return db.query(VehicleRental).all()


# GET RENTALS BY OWNER (PROVIDER)
@router.get("/owner/{owner_id}", response_model=list[VehicleRentalOut])
def get_rentals_by_owner(owner_id: int, db: Session = Depends(get_db)):
    from models.vehicle import Vehicle
    return db.query(VehicleRental).join(
        Vehicle, VehicleRental.vehicle_id == Vehicle.id
    ).filter(Vehicle.owner_id == owner_id).all()


# GET SINGLE RENTAL
@router.get("/{rental_id}", response_model=VehicleRentalOut)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(VehicleRental).filter(
        VehicleRental.id == rental_id
    ).first()

    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    return rental


# UPDATE RENTAL
@router.put("/{rental_id}", response_model=VehicleRentalOut)
def update_rental(
    rental_id: int,
    data: VehicleRentalUpdate,
    db: Session = Depends(get_db)
):
    rental = db.query(VehicleRental).filter(
        VehicleRental.id == rental_id
    ).first()

    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    # If status is updated to 'confirmed', mark vehicle as 'booked'
    # If status is updated to 'finished' or 'cancelled', mark vehicle as 'available'
    new_status = data.status.lower() if data.status else None
    
    from models.vehicle import Vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == rental.vehicle_id).first()

    for key, value in data.dict(exclude_unset=True).items():
        setattr(rental, key, value)

    if vehicle:
        if new_status in ["confirmed", "accepted"]:
            vehicle.availability = "booked"
        elif new_status in ["finished", "cancelled", "completed", "rejected"]:
            vehicle.availability = "available"

    db.commit()
    db.refresh(rental)
    return rental


# CANCEL RENTAL
@router.delete("/{rental_id}")
def cancel_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(VehicleRental).filter(
        VehicleRental.id == rental_id
    ).first()

    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")

    from models.vehicle import Vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == rental.vehicle_id).first()
    if vehicle:
        vehicle.availability = "available"

    rental.status = "cancelled"
    db.commit()

    return {"message": "Vehicle rental cancelled successfully"}
