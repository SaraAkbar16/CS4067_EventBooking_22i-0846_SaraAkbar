from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String

# PostgreSQL Database URL (update this with your actual credentials)
DATABASE_URL = "postgresql+asyncpg://postgres:sara2020@localhost/users"



# Create the database engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Base class for ORM models
Base = declarative_base()

# Define the Booking model
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    payment = Column(Integer, nullable=False)
    event = Column(Integer, nullable=False)

# Function to create tables (only run once)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
