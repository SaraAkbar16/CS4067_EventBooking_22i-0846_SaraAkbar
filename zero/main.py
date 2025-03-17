from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/main.html", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("zero.main:app", host="127.0.0.1", port=8000, reload=True)

