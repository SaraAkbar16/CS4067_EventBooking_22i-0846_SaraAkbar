import pika
import threading
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from third.database import SessionLocal, Booking, init_db
import sys
import os
from fastapi.responses import HTMLResponse
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from third.database import SessionLocal, Booking, init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
QUEUE_NAME = "task_queue"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

QUEUE_NAME = "task_queue"

def callback(ch, method, properties, body):
    print(f"Received Message: {body.decode()}")

def start_rabbitmq_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print("Waiting for messages. To exit, press CTRL+C")
    channel.start_consuming()

@app.on_event("startup")
async def startup_event():
    await init_db()
    thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    thread.start()

async def get_db():
    async with SessionLocal() as session:
        yield session

class BookingRequest(BaseModel):
    name: str
    payment: int
    event: int

@app.get("/")
async def serve_form(request: Request):
    event_ids = [1, 2, 3]  
    return templates.TemplateResponse("index2.html", {"request": request, "event_ids": event_ids})

@app.get("/index2", response_class=HTMLResponse)
async def index2(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})
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

        # Send booking details to RabbitMQ queue
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        message = f"Booking: {booking.name}, Payment: {booking.payment}, Event: {booking.event}"
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message)
        connection.close()

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
