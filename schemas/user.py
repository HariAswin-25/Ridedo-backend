from pydantic import BaseModel, field_validator
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    role: Optional[str] = "user"
    password: str
    confirm_password: str
    dob: Optional[str]
    
    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str]
    phone: Optional[str]
    dob: Optional[str]
    role: Optional[str]
    image_url: Optional[str]

class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    dob: Optional[str]
    role: str
    image_url: Optional[str]

    class Config:
        from_attributes = True
