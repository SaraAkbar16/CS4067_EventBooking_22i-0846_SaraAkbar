from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import sqlite3
import uvicorn

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Function to get DB connection
def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Route to serve the main page
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login route with database check
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user exists in the database
    cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return JSONResponse(content={"status": "success", "message": "Login successful"})
    else:
        return JSONResponse(content={"status": "fail", "message": "Invalid username or password"})
