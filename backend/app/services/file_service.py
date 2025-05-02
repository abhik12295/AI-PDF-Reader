from fastapi import UploadFile, HTTPException
from backend.app.db.supabase import supabase_client
import requests
import tempfile
from pdfminer.high_level import extract_text

def upload_pdf(file: UploadFile):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    response = supabase_client.storage.from_("uploads").upload(file.filename, file.file)
    if "error" in response:
        raise HTTPException(status_code=500, detail="File upload failed")
        
    return {"message": "File uploaded successfully", "file_url": response["Key"]}
