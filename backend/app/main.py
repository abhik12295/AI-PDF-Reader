from fastapi import FastAPI
from backend.app.routes import auth, dashboard



app = FastAPI()

#include routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def home():
    return {"message":"Welcome to FastApi Pdf with Supabase"}
