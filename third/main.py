import os
import asyncpg
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

DATABASE_URL = "postgresql://postgres:sara2020@localhost/users"

async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    db_pool = await create_pool()
    print("Database connection established!")
    yield
    await db_pool.close()
    print("Database connection closed.")

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})

class Booking(BaseModel):
    id: int
    name: str
    payment: int 
    event: int
# Correctly use the pool to get a connection
async def get_db_connection():
    async with db_pool.acquire() as conn:
        return conn

@app.post("/submit_form/")
async def submit_form(booking: Booking):
    try:
        # Get the database connection from the pool
        conn = await get_db_connection()

        # Insert the booking into the database
        query = """INSERT INTO bookings (name, payment, event) 
                   VALUES ($1, $2, $3) RETURNING id"""
        
        # Log the query and data being inserted for debugging
        print(f"Executing query: {query} with values: {booking.name}, {booking.payment}, {booking.event}")

        result = await conn.fetch(query, booking.name, booking.payment, booking.event)
        
        # Log the result to confirm if the ID is returned correctly
        print(f"Inserted booking with ID: {result[0]['id']}")

        # Commit the changes (auto-committed with asyncpg, so this isn't needed)
        await conn.close()

        # Return success with the booking data and generated ID
        return JSONResponse(content={
            "success": True,
            "data": {
                "id": result[0]["id"],
                "name": booking.name,
                "payment": booking.payment,
                "event": booking.event
            }
        })
    except Exception as e:
        # Log the full exception for better debugging
        print(f"Error occurred: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error saving booking to database: {str(e)}"
            }
        )
