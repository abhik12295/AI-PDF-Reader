import os
import json
import requests
from io import BytesIO
import http.client
import tempfile
from dotenv import load_dotenv
from starlette.datastructures import UploadFile
from fastapi import HTTPException
from backend.app.db.supabase import supabase_client
from pdfminer.high_level import extract_text as pdfminer_extract_text

# def upload_pdf(file: UploadFile):
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
#     response = supabase_client.storage.from_("uploads").upload(file.filename, file.file)
#     if "error" in response:
#         raise HTTPException(status_code=500, detail="File upload failed")
        
#     return {"message": "File uploaded successfully", "file_url": response["Key"]}


load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')

async def extract_pdf_text(pdf_file: UploadFile)-> str:
    if not isinstance(pdf_file, UploadFile):
        print(f"extract_pdf_text: Invalid input type: {type(pdf_file).__name__}, value: {pdf_file}")
        raise HTTPException(
            status_code=400,
            detail=f"Expected UploadFile, received {type(pdf_file).__name__} instead"
        )
    if not pdf_file.filename.lower().endswith('pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        content =  await pdf_file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        pdf_buffer = BytesIO(content)
        try:
            text = pdfminer_extract_text(pdf_buffer)
            if not text:
                raise HTTPException(status_code=400, detail= "No text can be extract from file")
            return text
        finally:
            pdf_buffer.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text text from PDF: {str(e)}")
    finally:
        await pdf_file.close()
    
def get_summary(text:str) -> str:
    """Summarize PDF content using GPT-4o via RapidAPI"""
    if len(text)>6000:
        text = text[:6000]
    
    payload = json.dumps({
        "model":"gpt-4o",
        "messages":[
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
        conn = http.client.HTTPSConnection("gpt-4o.p.rapidapi.com")
        conn.request("POST","/chat/completions", payload,headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if res.status!=200:
            raise HTTPException(
                status_code=500,
                detail=f"RapidAPI request failed with status {res.status}:{data}"
            )
        result = json.loads(data)
        if "choices" in result and len(result["choices"])>0:
            return result["choices"][0]["message"]["content"]
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected RAPIDAPI respose format: {data}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization Failed : {e}")


