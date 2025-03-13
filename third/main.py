import pika
import threading
import sys
import os
from fastapi import FastAPI, Request, Query, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

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

# Serve Registration Form
@app.get("/", response_class=HTMLResponse)
async def serve_form(request: Request):
    event_ids = [1, 2, 3]
    return templates.TemplateResponse("index2.html", {"request": request, "event_ids": event_ids})

@app.get("/index2", response_class=HTMLResponse)
async def index2(request: Request, name: str = Query(None), eventIds: str = Query(None)):
    selected_events = eventIds.split(",") if eventIds else []  # Convert CSV string to list
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

# Handle Booking Submission (without database logic)
@app.post("/submit/")
async def submit_form(name: str, payment: int, event: int):
    try:
        # Send booking details to RabbitMQ queue
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            message = f"Booking: {name}, Payment: {payment}, Event: {event}"
            channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=message)
            connection.close()
        except Exception as e:
            print(f"Error sending message to RabbitMQ: {e}")

        return {
            "success": True,
            "data": {
                "name": name,
                "payment": payment,
                "event": event
            }
        }
    except Exception as e:
        return {"success": False, "message": str(e)}