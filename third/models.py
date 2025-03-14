from sqlalchemy import Column, Integer, String
from database import Base

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    event_ids = Column(String)
