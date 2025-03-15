from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import asyncpg
import uvicorn

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# PostgreSQL Database Connection Settings
DATABASE_URL = "postgresql://postgres:sara2020@localhost:5432/users"

# Function to get DB connection
async def get_db_connection():
    return await asyncpg.connect(DATABASE_URL)

# Route to serve the main page (Fix: Return HTML Template)
@app.get("/")
async def main_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Register or login user
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = await get_db_connection()
    
    # Check if the username already exists
    existing_user = await conn.fetchrow("SELECT * FROM users WHERE name = $1", username)
    
    if existing_user:
        await conn.close()
        return JSONResponse(content={"status": "fail", "message": "Username already exists. Please choose another."})
    
    # Insert the new user into the database
    await conn.execute("INSERT INTO users (name, password) VALUES ($1, $2)", username, password)
    await conn.close()
    
    return JSONResponse(content={"status": "success", "message": "User registered successfully!", "redirect_url": "http://127.0.0.1:8001"})

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
