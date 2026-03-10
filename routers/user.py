from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from db.database import get_db
from models.user import User
from models.cab_booking import CabBooking
from models.vehicle_rental import VehicleRental
from models.driver_booking import DriverBooking
from schemas.user import UserCreate, UserUpdate, UserOut
from schemas.activity import UserActivity
from utils.cloudinary_utils import upload_image

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    # Extract only the fields needed for User model (exclude confirm_password)
    user_data = user.dict(exclude={'confirm_password'})
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/create-provider", response_model=UserOut)
async def create_provider(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    role: str = Form("rental_provider"),
    dob: Optional[str] = Form(""),
    image_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    image_url = None
    if image_file:
        image_url = upload_image(image_file.file)
        if not image_url:
            raise HTTPException(400, "Image upload to Cloudinary failed")

    new_user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password=password,
        role=role,
        dob=dob,
        image_url=image_url
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

from schemas.user import UserLogin

@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if db_user.password != user.password:
        raise HTTPException(status_code=400, detail="Invalid password")

    return {"message": "Login successful", "id": db_user.id, "role": db_user.role}

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # delete child records first (important)
    db.execute(text("DELETE FROM cab_bookings WHERE user_id = :uid"), {"uid": user_id})
    db.execute(text("DELETE FROM driver_bookings WHERE user_id = :uid"), {"uid": user_id})
    db.execute(text("DELETE FROM vehicle_rentals WHERE user_id = :uid"), {"uid": user_id})

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

@router.get("/{user_id}/activity", response_model=UserActivity)
def get_user_activity(user_id: int, db: Session = Depends(get_db)):
    cab_bookings = db.query(CabBooking).filter(CabBooking.user_id == user_id).all()
    vehicle_rentals = db.query(VehicleRental).filter(VehicleRental.user_id == user_id).all()
    driver_bookings = db.query(DriverBooking).filter(DriverBooking.user_id == user_id).all()
    
    return {
        "cab_bookings": cab_bookings,
        "vehicle_rentals": vehicle_rentals,
        "driver_bookings": driver_bookings
    }
