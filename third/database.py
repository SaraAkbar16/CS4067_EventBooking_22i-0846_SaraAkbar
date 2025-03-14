from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

# PostgreSQL Database URL (Ensure your credentials are correct)
DATABASE_URL = "postgresql://postgres:sara2020@localhost/users"

# Set up database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the Booking table
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    payment = Column(Integer, nullable=False)
    event = Column(Integer, nullable=False)

# Ensure table creation
Base.metadata.create_all(bind=engine)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define Pydantic model for request validation
class BookingData(BaseModel):
    name: str  # Updated to match the `Booking` table
    event: int
    payment: int
