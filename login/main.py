from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
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

# Route to serve the main page
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Login route with database check
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = await get_db_connection()
    
    # Check if the user exists in the database
    user = await conn.fetchrow("SELECT * FROM users WHERE name = $1 AND password = $2", username, password)
    
    await conn.close()

    if user:
        # Attach the username to the redirect URL
        return JSONResponse(content={"status": "success", "redirect_url": f"http://127.0.0.1:8001/index1.html?username={username}"})
    else:
        return JSONResponse(content={"status": "fail", "message": "Invalid username or password"})

# Run the FastAPI app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
