from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from backend.app.services.auth_service import register_user, login_user, logout_user
from backend.app.models import UserCreate, UserLogin
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.db.supabase import JWT_KEY
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Form
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import jwt
from pydantic import EmailStr

router = APIRouter()

# Path to the base directory (adjusted to ensure the correct path)

app = FastAPI()

BASE_DIR = Path(r"C:\Users\stuar\Desktop\AI PDF fastapi")

# Mount static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend/static"), name="static")

# Load templates
templates = Jinja2Templates(directory=BASE_DIR / "frontend/templates")

# Serve the signup page
@router.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

# Router
@router.post("/signup")
#async def signup(user: UserCreate):
async def signup(email: EmailStr = Form(...), password: str = Form(...)):
    print(f"Received user data: {email}, {password}")
    try:
        return register_user(email, password)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")


# Serve the login page
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
#async def login(user: UserLogin, response: Response):
async def login(response: Response, email: EmailStr = Form(...), password = Form(...)):
    try:
        return login_user(email, password, response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


# Serve the dashboard page
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


#@router.get("/logout")
@router.get("/logout")
async def logout(response: Response):
    try:
        return logout_user(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout failed: {str(e)}")
