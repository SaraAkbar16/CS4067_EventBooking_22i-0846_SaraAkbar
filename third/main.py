from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from third.database import SessionLocal, Booking, init_db

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Ensure database tables are created
@app.on_event("startup")
async def startup_event():
    await init_db()

# Dependency to get database session
async def get_db():
    async with SessionLocal() as session:
        yield session

# Pydantic model for request body
class BookingRequest(BaseModel):
    name: str
    payment: int
    event: int

@app.get("/")
async def serve_form(request: Request):
    event_ids = [1, 2, 3]  
    return templates.TemplateResponse("index2.html", {"request": request, "event_ids": event_ids})

@app.post("/submit/")
async def submit_form(booking: BookingRequest, db: AsyncSession = Depends(get_db)):
    try:
        new_booking = Booking(
            name=booking.name,
            payment=booking.payment,
            event=booking.event
        )
        db.add(new_booking)
        await db.commit()
        await db.refresh(new_booking)

        return {
            "success": True,
            "data": {
                "id": new_booking.id,
                "name": booking.name,
                "payment": booking.payment,
                "event": booking.event
            }
        }

    except Exception as e:
        return {"success": False, "message": str(e)}
