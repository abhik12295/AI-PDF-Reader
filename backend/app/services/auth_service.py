import jwt
import bcrypt
from datetime import datetime, timedelta
from backend.app.utils.config import config
from backend.app.db.supabase import supabase_client

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"

def create_jwt(data: dict):
    expire = datetime.now(datetime.timezone.utc)+ timedelta(hours=1)
    data.update({"exp":expire})
    return jwt.encode(data, SECRET_KEY, algorithm= ALGORITHM)

def signup_user(user):
    user.password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
    response = supabase_client.auth.sign_up({
        "email":user.email, 
        "password":user.password
    })
    return response

def login_user(user):
    response = supabase_client.auth.sign_in_with_password({
        "email": user.email,
        "password": user.pasword
    })
    if response.get("session"):
        return {"token": create_jwt({"sub":user.email})}

    return {"error": "Invalid credentials"}
