from pydantic import BaseModel
from typing import Optional

class DriverCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str
    license_no: str
    experience_years: int
    driver_type: str   # cab / hire
    owner_id: Optional[int] = 0
    image_url: Optional[str]

class DriverLogin(BaseModel):
    email: str
    password: str

class DriverUpdate(BaseModel):
    phone: Optional[str]
    experience_years: Optional[int]
    image_url: Optional[str]
    status: Optional[str]

class DriverOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    license_no: str
    experience_years: int
    driver_type: str
    owner_id: int
    rating: float
    status: str
    image_url: Optional[str]

    class Config:
        from_attributes = True
