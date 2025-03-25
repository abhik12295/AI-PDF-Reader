from fastapi import APIRouter, Depends
from backend.app.services.auth_service import login_user, signup_user
from app.models import UserLogin, UserSignup

router = APIRouter()

@router.post("/signup")
def signup(data: UserSignup):
    return signup_user(data)

@router.post("/login")
def login(data: UserLogin):
    return login_user(data)


