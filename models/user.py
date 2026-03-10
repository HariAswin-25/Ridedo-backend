from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    dob = Column(String)
    phone = Column(String, nullable=False)
    role = Column(String, default="user") # 'user', 'driver', 'cab_driver', 'rental_provider'
    image_url = Column(String)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
