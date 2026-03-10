from db.database import SessionLocal
from datetime import datetime, timezone
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def utcnow() -> datetime:
    """Returns the current time in UTC."""
    return datetime.now(timezone.utc)
