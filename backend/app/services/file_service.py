import requests
import tempfile
from fastapi import UploadFile, HTTPException
from backend.app.db.supabase import supabase_client
from pdfminer.high_level import extract_text
from dotenv import load_dotenv
import os
import json
import http.client

# def upload_pdf(file: UploadFile):
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
#     response = supabase_client.storage.from_("uploads").upload(file.filename, file.file)
#     if "error" in response:
#         raise HTTPException(status_code=500, detail="File upload failed")
        
#     return {"message": "File uploaded successfully", "file_url": response["Key"]}


load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

def extract_text(pdf_file: UploadFile)-> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
            content = pdf_file.file.read()
            tmp.write(content)
            tmp.flush()
            text = extract_text(tmp.name)
            return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text text from PDF: {str(e)}")
    
def get_summary(text:str) -> str:
    """Summarize PDF content using GPT-4o via RapidAPI"""
    if len(text)>6000:
        text = text[:6000]
    
    payload = json.dumps({
        "model":"gpt-4o",
        "message":[
            {"role":"system","content":"You are an AI assistant that summarizes PDF content."},
            {"role":"user","content":f"Please summarize the following PDF content:\n\n{text}"}
        ]
    })

    headers = {
        'x-rapidapi-key':RAPIDAPI_KEY,
        'x-rapidapi-host':"gpt-4o.p.rapidapi.com",
        'Content-Type':"application/json"
    }

    try:
        conn = http.client.HTTPConnection("gpt-4o.p.rapidapi.com")
        conn.request("POST","/chat/completions", body=payload,headers=headers)
        res = conn.getresponse()
        data = res.read()
        result = json.loads(data.decode("utf-8"))
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization Failed : {e}")


