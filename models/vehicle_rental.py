from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Time,
    DateTime,
    ForeignKey
)
from db.database import Base
from datetime import datetime


class VehicleRental(Base):
    __tablename__ = "vehicle_rentals"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)

    pickup_location = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    driving_license_number = Column(String, nullable=False)

    pickup_date = Column(Date, nullable=False)
    pickup_time = Column(Time, nullable=False)

    return_date = Column(Date, nullable=False)
    return_time = Column(Time, nullable=False)

    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
