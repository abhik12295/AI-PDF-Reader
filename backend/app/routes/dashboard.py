from fastapi import APIRouter, Depends, UploadFile, File
from app.services.file_service import upload_file

router = APIRouter()

@router.post("/upload")
def upload(file: UploadFile = File(...)):
    return None