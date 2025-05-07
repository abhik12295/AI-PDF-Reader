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
import hashlib

load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
SUPABASE_PROJECT_ID = os.getenv('SUPABASE_PROJECT_ID')
SUPASBASE_STORAGE_ENDPOINT = f'https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/s3'

async def extract_pdf_text(content: bytes, filename: str)-> str:
    if not filename.lower().endswith('pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty")
    try:
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


# Adding feature upload pdf to storage
async def upload_pdf_to_storage(pdf_file:UploadFile,content:bytes, user_email:str)->str:
    #upload pdf to storage and save metadata in user_pdfs table
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400,detail="Only pdf files are allowed")
    if not content:
        raise HTTPException(status_code=400,detail="Uploaded PDF is empty")
    
    #hash the file
    file_hash = hashlib.sha256(content).hexdigest()

    #get user_id
    user_data = supabase_client.table("pdf_user").select("id").eq("email", user_email).execute()
    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user_data.data[0]["id"]

    #check for duplicate files
    hash_check = supabase_client.table("user_pdfs").select("id").eq("file_hash", file_hash).execute()
    if hash_check.data:
        raise HTTPException(status_code=400, detail="File already exists")
    
    #check PDF limit(5 per user)
    pdf_count = supabase_client.table("user_pdfs").select("id", count="exact").eq("user_id",user_id).execute()
    count = pdf_count.count if hasattr(pdf_count, 'count') else len(pdf_count.data)
    if count>=5:
        raise HTTPException(status_code=400,detail="Maximum 5 pdfs per user reached")
    
    #upload to storage supabase
    file_path = f"{user_id}/{pdf_file.filename}"
    try:
        response = supabase_client.storage.from_("pdf-upload").upload(
            file_path,content, file_options={"content_type":"application/pdf"}
            )
        if hasattr(response, 'error') and response.error:
            raise HTTPException(status_code=500, detail=f"File upload failed: {response.error}")
        
        #generate public url
        pdf_url = f"{SUPASBASE_STORAGE_ENDPOINT}/pdf-upload/{file_path}"       

        #save metadata
        pdf_data = {
            "user_id":user_id,
            "file_name":pdf_file.filename,
            "pdf_url":pdf_url,
            "file_hash":file_hash
        } 
        insert_response = supabase_client.table("user_pdfs").insert(pdf_data).execute()
        if not insert_response.data:
            # Rollback upload
            supabase_client.storage.from_("pdf-upload").remove([file_path])
            raise HTTPException(status_code=500, detail="Failed to save pdf metadata")
        return {
            "message":"File uploaded successfully",
            "file_name": pdf_file.filename,
            "pdf_url":pdf_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed : {str(e)}")
    finally:
        await pdf_file.close()
    
async def delete_pdf_from_storage(pdf_id: int, user_email:str)-> dict:
    # get user data
    user_data = supabase_client.table("pdf_user").select("id").eq("email",user_email).execute()
    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user_data.data[0]["id"]

    # get pdf data
    pdf_data = supabase_client.table("user_pdfs").select("file_name, user_id").eq("id", pdf_id).execute()
    if not pdf_data.data:
        raise HTTPException(status_code=404, detail="PDF not found")
    if pdf_data.data[0]["user_id"]!=user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this PDF")
    file_name = pdf_data.data[0]["file_name"]

    # get path for pdf
    file_path = f"{user_id}/{file_name}"

    try:
        response = supabase_client.storage.from_("pdf-upload").remove([file_path])
        if hasattr(response, 'error') and response.error:
            raise HTTPException(status_code=500, detail=f"File deletion failed {response.error}")
        
        supabase_client.table("user_pdfs").delete().eq("id",pdf_id).execute()
        return {"message":f"File {file_name} delete successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
    
async def get_user_pdfs(user_email:str)->list:
    # get list of user pdfs
    user_data = supabase_client.table("pdf_user").select("id").eq("email",user_email).execute()
    if not user_data.data:
        raise HTTPException(status_code=404,detail="User not found")
    user_id = user_data.data[0]["id"]

    pdfs = supabase_client.table("user_pdfs"
                        ).select("id, file_name,pdf_url,created_at").eq("user_id",user_id).order("created_at",desc=True).execute()
    return pdfs.data or []

