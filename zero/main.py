from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

app = FastAPI()

# Serve static files from the 'static' directory (e.g., styles.css)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates for the 'templates' directory
templates = Jinja2Templates(directory="templates")


# Route to serve the 'main.html' page
@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

# Run the app
if __name__ == "__main__":
    uvicorn.run("first.main:app", host="127.0.0.1", port=8000, reload=True)
