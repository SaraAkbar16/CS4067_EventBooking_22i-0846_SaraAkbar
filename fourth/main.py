from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pymongo import MongoClient
import uvicorn

app = FastAPI()

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["sms"]
collection = db["sms"]

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/messages")
async def get_messages():
    messages = list(collection.find({}, {"_id": 0}))
    if not messages:
        return {"messages": [{"text": "No messages found."}]} 
    return {"messages": messages}

# Serve index3.html from templates
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index3.html", {"request": request})

# Serve static files if needed
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run("fourth.main:app", host="127.0.0.1", port=8000, reload=True)
