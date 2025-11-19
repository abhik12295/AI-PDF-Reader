from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os
import sys
from backend.app.core.config import BASE_DIR
from backend.app.routes import auth, dashboard
from backend.app.auth_config import auth_middleware, get_current_user

sys.path.append(str(BASE_DIR))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware('http')(auth_middleware)

app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend" / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "frontend" / "templates")


app.include_router(auth.router)
app.include_router(dashboard.router, prefix="/dashboard")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


# Production server - Changes 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)