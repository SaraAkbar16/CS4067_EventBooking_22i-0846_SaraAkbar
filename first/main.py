import webbrowser
import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from first.database import engine, SessionLocal
import first.models as models
import first.schemas as schemas
from fastapi.responses import RedirectResponse
import threading
from fastapi import HTTPException
import requests
from fastapi.responses import HTMLResponse
import sys
import os;
from typing import Optional
app = FastAPI()
#dsfgbvcsw
#login done
# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if the username already exists
    existing_user = db.query(models.User).filter(models.User.name == user.name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists. Please choose another one.")

    # Create new user
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Return JSON response with redirect URL
    return {"redirect_url": f"/welcome?name={db_user.name}"}


# Function to open browser
def open_browser():
    webbrowser.open("http://127.0.0.1:8000")

@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Return JSON response with redirect URL
    return {"redirect_url": f"/welcome?name={db_user.name}"}

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

@app.get("/events")
def get_events():
    try:
        print("🔄 Fetching events from Java API...")
        response = requests.get(SPRING_BOOT_API)
        
        if response.status_code == 404:
            print("⚠️ No events found in Java API.")
            return {"message": "No events available."}
        
        response.raise_for_status() 
        print("✅ Events successfully fetched from Java API.")
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"🚨 Error fetching events: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch events from Java API")
    
@app.get("/index2", response_class=HTMLResponse)
async def index2(request: Request, event_ids: Optional[int] = None):
    return templates.TemplateResponse("/index2.html", {"request": request})


from pydantic import BaseModel  # Import BaseModel
from fastapi.responses import JSONResponse


class EventData(BaseModel):
    event_ids: list[int]

@app.post("/process_event")
async def process_event(data: EventData):
    try:
        print(f"Received event IDs: {data.event_ids}")
        # Process event IDs here
        return {"success": True, "message": "Events processed successfully"}
        return RedirectResponse(url="index3.html", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error processing events")

@app.get("/index3", response_class=HTMLResponse)
async def index3(request: Request):
    return RedirectResponse(url="/static/index3.html", status_code=303)

if __name__ == "__main__":
    uvicorn.run("first.main:app", host="127.0.0.1", port=8000, reload=True)