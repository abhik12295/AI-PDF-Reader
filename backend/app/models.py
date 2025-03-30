from pydantic import BaseModel, EmailStr
from fastapi import Form

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
