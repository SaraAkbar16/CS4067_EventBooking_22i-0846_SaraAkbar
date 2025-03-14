import uvicorn
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from first.database import engine, SessionLocal
from first import models
import first.schemas as schemas
import requests
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
import os
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Template directory
templates = Jinja2Templates(directory="templates")

# Create tables
models.Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    name: str
    password: str

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/users/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(name=user_data.name, password=user_data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Redirect to the welcome page with the username as a query parameter
    return RedirectResponse(url=f"/welcome?name={new_user.name}", status_code=303)

@app.get("/welcome")
def welcome_page(request: Request, name: str = "Guest"):
    return templates.TemplateResponse("welcome.html", {"request": request, "name": name})

@app.get("/{page}")
def serve_page(request: Request, page: str, name: str = "Guest"):
    if page not in ["welcome", "index1.html"]:
        return {"detail": "Not Found"}
    return templates.TemplateResponse(f"{page}", {"request": request, "name": name})

@app.get("/check_user")
def check_user(name: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.name == name).first()
    return {"exists": user is not None}

SPRING_BOOT_API = "http://127.0.0.1:8080/api/events"

@app.get("/events", response_class=HTMLResponse)
def get_events(request: Request):
    try:
        response = requests.get(SPRING_BOOT_API)
        response.raise_for_status()
        events = response.json()
        
        return templates.TemplateResponse("index1.html", {"request": request, "events": events})
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=500, detail="Failed to fetch events from Java API")

@app.get("/index2", response_class=HTMLResponse)
async def index2(request: Request, event_ids: Optional[int] = None):
    return templates.TemplateResponse("/index2.html", {"request": request})

class EventData(BaseModel):
    event_ids: list[int]

@app.post("/process_event")
async def process_event(data: EventData):
    return {"success": True, "message": "Events processed successfully"}

@app.get("/index3", response_class=HTMLResponse)
async def index3(request: Request):
    return RedirectResponse(url="/static/index3.html", status_code=303)

if __name__ == "__main__":
    uvicorn.run("first.main:app", host="127.0.0.1", port=8000, reload=True)