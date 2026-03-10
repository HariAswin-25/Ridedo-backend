from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True) # User who posted the vehicle

    vehicle_type = Column(String, nullable=False)   # car / bike
    vehicle_name = Column(String, nullable=False)
    vehicle_number = Column(String, nullable=False, unique=True)

    fuel_type = Column(String, nullable=False)
    rent_per_day = Column(Integer, nullable=False)

    availability = Column(String, default="available")  # available / booked
    image_url = Column(String, nullable=True)
