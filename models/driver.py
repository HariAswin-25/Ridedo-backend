from sqlalchemy import Column, Integer, String, Float, DateTime
from db.database import Base
from datetime import datetime

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    license_no = Column(String, nullable=False)
    experience_years = Column(Integer)
    owner_id = Column(Integer, default=0) # 0 for independent, others for rental providers
    driver_type = Column(String)  # cab / hire
    image_url = Column(String)
    status = Column(String, default="available")
    rating = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
