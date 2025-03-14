from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import get_db, Booking, BookingData

from fastapi.middleware.cors import CORSMiddleware
import pika
import threading
import sys
import os
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request, Query, WebSocket, HTTPException


sys.path.append(os.path.abspath(os.path.dirname(__file__)))

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
def startup_event():
    thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    thread.start()

@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    event_ids = [1, 2, 3]
    return templates.TemplateResponse("index2.html", {"request": request, "event_ids": event_ids})

@app.get("/index2", response_class=HTMLResponse)
async def index2(request: Request, name: str = Query(None), eventIds: str = Query(None)):
    selected_events = eventIds.split(",") if eventIds else []  
    return templates.TemplateResponse(
        "index2.html", 
        {"request": request, "name": name, "selected_events": selected_events}
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Received: {data}")

@app.post("/submit/")
async def submit_form(data: BookingData, db: Session = Depends(get_db)):
    try:
        # Insert booking details into PostgreSQL
        new_booking = Booking(name=data.name, payment=data.payment, event=data.event)
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)

        # Send booking details to RabbitMQ queue
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            message = f"Booking: {data.name}, Payment: {data.payment}, Event: {data.event}"
            channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=message)
            connection.close()
        except Exception as e:
            print(f"Error sending message to RabbitMQ: {e}")

        return {
            "success": True,
            "data": {
                "id": new_booking.id,
                "name": new_booking.name,
                "payment": new_booking.payment,
                "event": new_booking.event
            }
        }
    except Exception as e:
        db.rollback() 
        return {"success": False, "message": str(e)}
