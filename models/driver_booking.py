from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from db.database import Base
from datetime import datetime

class DriverBooking(Base):
    __tablename__ = "driver_bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=True)

    pickup_location = Column(String, nullable=False)
    drop_location = Column(String, nullable=False)

    booking_date = Column(String, nullable=False)
    booking_time = Column(String, nullable=False)

    duration_hours = Column(Integer, nullable=False)
    contact_number = Column(String, nullable=False)

    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
