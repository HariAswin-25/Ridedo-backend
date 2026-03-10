from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import json
from typing import Optional
from sqlalchemy.orm import Session
from db.database import get_db
from models.driver import Driver
from schemas.driver import DriverCreate, DriverLogin, DriverOut, DriverUpdate
from utils.cloudinary_utils import upload_image

router = APIRouter(prefix="/drivers", tags=["Drivers"])

@router.post("/create", response_model=DriverOut)
async def create_driver(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    license_no: str = Form(...),
    experience_years: int = Form(...),
    driver_type: str = Form(...),
    owner_id: int = Form(0),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Check if driver already exists
    existing = db.query(Driver).filter(Driver.email == email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    image_url = None
    if image_file:
        image_url = upload_image(image_file.file)
        if not image_url:
            raise HTTPException(400, "Image upload to Cloudinary failed. Check credentials.")

    new_driver = Driver(
        full_name=full_name,
        email=email,
        phone=phone,
        password=password,
        license_no=license_no,
        experience_years=experience_years,
        driver_type=driver_type,
        owner_id=owner_id,
        image_url=image_url
    )
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    return new_driver

def sync_driver_availability(db: Session):
    """Automatically mark drivers as available if their booking duration has ended."""
    try:
        from datetime import datetime, timedelta
        from models.driver import Driver
        from models.driver_booking import DriverBooking
        
        now = datetime.utcnow()
        
        # Get all 'confirmed' or 'accepted' bookings for Manual Hire
        active_bookings = db.query(DriverBooking).filter(
            DriverBooking.status.in_(["confirmed", "accepted"])
        ).all()

        updated_count = 0
        for booking in active_bookings:
            try:
                # Assuming booking_date is 'YYYY-MM-DD' and booking_time is 'HH:MM'
                # Let's try to parse them
                start_dt = datetime.strptime(f"{booking.booking_date} {booking.booking_time}", "%Y-%m-%d %H:%M")
                end_dt = start_dt + timedelta(hours=booking.duration_hours)

                if now >= end_dt:
                    booking.status = "finished"
                    driver = db.query(Driver).filter(Driver.id == booking.driver_id).first()
                    if driver:
                        driver.status = "available"
                    updated_count += 1
            except Exception as parse_err:
                print(f"DEBUG: Could not parse booking {booking.id} time: {parse_err}")
                continue

        if updated_count > 0:
            db.commit()
            print(f"DEBUG: Synchronized {updated_count} drivers to available.")

    except Exception as e:
        print(f"ERROR in sync_driver_availability: {e}")
        db.rollback()

@router.get("/owner/{owner_id}", response_model=list[DriverOut])
def get_drivers_by_owner(owner_id: int, db: Session = Depends(get_db)):
    sync_driver_availability(db)
    return db.query(Driver).filter(Driver.owner_id == owner_id).all()

@router.get("/all", response_model=list[DriverOut])
def get_all_drivers(db: Session = Depends(get_db)):
    sync_driver_availability(db)
    return db.query(Driver).all()

@router.post("/login")
def login_driver(data: DriverLogin, db: Session = Depends(get_db)):
    driver = db.query(Driver).filter(
        Driver.email == data.email,
        Driver.password == data.password
    ).first()
    if not driver:
        raise HTTPException(401, "Invalid credentials")
    return {"message": "Login successful", "driver_id": driver.id}

@router.get("/", response_model=list[DriverOut])
def get_drivers(db: Session = Depends(get_db)):
    sync_driver_availability(db)
    return db.query(Driver).filter(Driver.status == "available").all()

@router.put("/{driver_id}", response_model=DriverOut)
async def update_driver(
    driver_id: int,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    license_no: Optional[str] = Form(None),
    experience_years: Optional[int] = Form(None),
    driver_type: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(404, "Driver not found")
    
    if full_name: driver.full_name = full_name
    if email: driver.email = email
    if phone: driver.phone = phone
    if password: driver.password = password
    if license_no: driver.license_no = license_no
    if experience_years is not None: driver.experience_years = experience_years
    if driver_type: driver.driver_type = driver_type
    if status: driver.status = status

    if image_file:
        print(f"Uploading image for driver {driver_id}...")
        image_url = upload_image(image_file.file)
        if image_url:
            print(f"New image URL: {image_url}")
            driver.image_url = image_url
        else:
            print("Image upload failed.")
            raise HTTPException(status_code=400, detail="Image upload to Cloudinary failed")
        
    db.commit()
    db.refresh(driver)
    return driver

@router.delete("/{driver_id}")
def delete_driver(driver_id: int, db: Session = Depends(get_db)):
    driver = db.query(Driver).get(driver_id)
    if not driver:
        raise HTTPException(404, "Driver not found")
    db.delete(driver)
    db.commit()
    return {"message": "Driver deleted"}
