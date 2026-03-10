from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from dependencies import get_db
from models.vehicle import Vehicle
from models.user import User
from schemas.vehicle import VehicleUpdate, VehicleOut
from utils.cloudinary_utils import upload_image

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

def sync_vehicle_availability(db: Session):
    """Automatically mark vehicles as available if their rental duration has ended."""
    try:
        from datetime import datetime
        from models.vehicle_rental import VehicleRental
        from models.vehicle import Vehicle
        
        now = datetime.utcnow()
        today = now.date()
        current_time = now.time()

        # Find all 'confirmed' rentals
        active_rentals = db.query(VehicleRental).filter(
            VehicleRental.status == "confirmed"
        ).all()

        expired_count = 0
        for rental in active_rentals:
            # If return date is in the past OR return date is today but return time is in the past
            if rental.return_date < today or (rental.return_date == today and rental.return_time <= current_time):
                rental.status = "finished"
                vehicle = db.query(Vehicle).filter(Vehicle.id == rental.vehicle_id).first()
                if vehicle:
                    vehicle.availability = "available"
                expired_count += 1
        
        if expired_count > 0:
            db.commit()
            print(f"DEBUG: Synchronized {expired_count} vehicles to available.")
    except Exception as e:
        print(f"ERROR in sync_vehicle_availability: {e}")
        db.rollback()


# READ ALL (Admin Only)
@router.get("/all", response_model=list[VehicleOut])
def get_all_vehicles_admin(db: Session = Depends(get_db)):
    print("DEBUG: Hit get_all_vehicles_admin")
    sync_vehicle_availability(db)
    return db.query(Vehicle).all()


# CREATE
@router.post("/create", response_model=VehicleOut)
async def add_vehicle(
    vehicle_type: str = Form(...), # car / bike
    vehicle_name: str = Form(...),
    vehicle_number: str = Form(...),
    fuel_type: str = Form(...),
    rent_per_day: int = Form(...),
    owner_id: Optional[int] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Check if owner exists if owner_id provided
    if owner_id:
        user = db.query(User).filter(User.id == owner_id).first()
        if not user:
             raise HTTPException(status_code=404, detail="Owner user not found")

    image_url = None
    if image_file:
        image_url = upload_image(image_file.file)
        if not image_url:
            raise HTTPException(status_code=400, detail="Image upload to Cloudinary failed")

    vehicle = Vehicle(
        vehicle_type=vehicle_type,
        vehicle_name=vehicle_name,
        vehicle_number=vehicle_number,
        fuel_type=fuel_type,
        rent_per_day=rent_per_day,
        owner_id=owner_id,
        image_url=image_url,
        availability="available"
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


# READ ALL (Available only)
@router.get("/", response_model=list[VehicleOut])
def get_all_vehicles(db: Session = Depends(get_db)):
    print("DEBUG: Hit get_all_vehicles")
    sync_vehicle_availability(db)
    return db.query(Vehicle).filter(Vehicle.availability == "available").all()


# ✅ FILTER – CARS (STATIC FIRST)
@router.get("/cars", response_model=list[VehicleOut])
def get_cars(db: Session = Depends(get_db)):
    print("DEBUG: Hit get_cars")
    sync_vehicle_availability(db)
    return db.query(Vehicle).filter(Vehicle.vehicle_type == "car").all()


# ✅ FILTER – BIKES (STATIC FIRST)
@router.get("/bikes", response_model=list[VehicleOut])
def get_bikes(db: Session = Depends(get_db)):
    print("DEBUG: Hit get_bikes")
    sync_vehicle_availability(db)
    return db.query(Vehicle).filter(Vehicle.vehicle_type == "bike").all()


# READ ONE (DYNAMIC LAST)
@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


# UPDATE
@router.put("/{vehicle_id}", response_model=VehicleOut)
async def update_vehicle(
    vehicle_id: int,
    vehicle_name: Optional[str] = Form(None),
    vehicle_number: Optional[str] = Form(None),
    vehicle_type: Optional[str] = Form(None),
    fuel_type: Optional[str] = Form(None),
    rent_per_day: Optional[int] = Form(None),
    availability: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle_name: vehicle.vehicle_name = vehicle_name
    if vehicle_number: vehicle.vehicle_number = vehicle_number
    if vehicle_type: vehicle.vehicle_type = vehicle_type
    if fuel_type: vehicle.fuel_type = fuel_type
    if rent_per_day is not None: vehicle.rent_per_day = rent_per_day
    if availability: vehicle.availability = availability

    if image_file:
        print(f"Uploading image for vehicle {vehicle_id}...")
        image_url = upload_image(image_file.file)
        if image_url:
            print(f"New image URL: {image_url}")
            vehicle.image_url = image_url
        else:
            print("Image upload failed.")
            raise HTTPException(status_code=400, detail="Image upload to Cloudinary failed")

    db.commit()
    db.refresh(vehicle)
    return vehicle


# DELETE
@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}
