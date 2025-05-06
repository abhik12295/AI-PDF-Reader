from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.app.routes import auth, dashboard
from backend.app.auth_config import auth_middleware
from pathlib import Path
from backend.app.auth_config import get_current_user

app = FastAPI()
print("Starting FastAPI app")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware('http')(auth_middleware)

# Define the base directory to match your actual file structure
BASE_DIR = Path(r"C:\Users\stuar\Desktop\AI PDF fastapi")
# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend/static"), name="static")
# Load templates
templates = Jinja2Templates(directory=BASE_DIR / "frontend/templates")

# Include Routes
app.include_router(auth.router)
app.include_router(dashboard.router,prefix="/dashboard")
# app.include_router(dashboard_router)

# Serve the index page
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
