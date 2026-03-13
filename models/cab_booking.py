from sqlalchemy import Column, Integer, String, ForeignKey, Date, Time, DateTime
from db.database import Base
from datetime import datetime

class CabBooking(Base):
    __tablename__ = "cab_bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True) # Assigned driver

    pickup_location = Column(String, nullable=False)
    destination = Column(String, nullable=False)

    cab_type = Column(String, nullable=False)
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)

    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
