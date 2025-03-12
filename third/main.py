import pika
import threading
import sys
import os
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from third.database import SessionLocal, Booking, init_db

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

app = FastAPI()
QUEUE_NAME = "task_queue"

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


# RabbitMQ Consumer
def callback(ch, method, properties, body):
    print(f"Received Message: {body.decode()}")


def start_rabbitmq_consumer():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
        print("Waiting for messages. To exit, press CTRL+C")
        channel.start_consuming()
    except Exception as e:
        print(f"Error starting RabbitMQ consumer: {e}")


@app.on_event("startup")
async def startup_event():
    await init_db()
    thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    thread.start()


# Dependency for database session
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Pydantic Model for Booking
class BookingRequest(BaseModel):
    name: str
    payment: int
    event: int


# Serve Registration Form
@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    event_ids = [1, 2, 3]
    return templates.TemplateResponse("index2.html", {"request": request, "event_ids": event_ids})
from fastapi import Query

@app.get("/index2", response_class=HTMLResponse)
async def index2(request: Request, name: str = Query(None), eventIds: str = Query(None)):
    selected_events = eventIds.split(",") if eventIds else []  # Convert CSV string to list
    return templates.TemplateResponse(
        "index2.html", 
        {"request": request, "name": name, "selected_events": selected_events}
    )




# Handle Booking Submission
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
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            message = f"Booking: {booking.name}, Payment: {booking.payment}, Event: {booking.event}"
            channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=message)
            connection.close()
        except Exception as e:
            print(f"Error sending message to RabbitMQ: {e}")

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
