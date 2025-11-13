import os
import json
from io import BytesIO
import http.client
from dotenv import load_dotenv
from starlette.datastructures import UploadFile
from fastapi import HTTPException
from backend.app.db.supabase import supabase_client
from pdfminer.high_level import extract_text as pdfminer_extract_text
import hashlib
import logging
from urllib.parse import quote, unquote
import re
import os
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

# Configure logging
logging.basicConfig(level=logging.DEBUG) 
# Suppress few logs like httpx, httpcore logs
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('hpack').setLevel(logging.WARNING)
logging.getLogger('pdfminer').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


load_dotenv()
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
SUPABASE_PROJECT_ID = os.getenv('SUPABASE_PROJECT_ID')
SUPABASE_STORAGE_ENDPOINT = f'https://{SUPABASE_PROJECT_ID}.supabase.co/storage/v1/object/public'

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

# Test function to check if the API is working
def ask_question_about_summary(summary: str, question: str) -> str:
    """Ask a question about the PDF summary using GPT-4o via RapidAPI"""
    if len(summary) > 6000:
        summary = summary[:6000]
    
    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are an AI assistant that answers questions based on a PDF summary."},
            {"role": "user", "content": f"Based on the following PDF summary:\n\n{summary}\n\nAnswer the question: {question}"}
        ]
    })

    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': "gpt-4o.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    try:
        conn = http.client.HTTPSConnection("gpt-4o.p.rapidapi.com")
        conn.request("POST", "/chat/completions", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        if res.status != 200:
            raise HTTPException(
                status_code=500,
                detail=f"RapidAPI request failed with status {res.status}: {data}"
            )
        result = json.loads(data)
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected RapidAPI response format: {data}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question answering failed: {str(e)}")

# # Adding feature upload pdf to storage 
# async def upload_pdf_to_storage(pdf_file:UploadFile,content:bytes, user_email:str,full_text: str, summary: str)->dict:
#     #upload pdf to storage and save metadata in user_pdfs table
#     if not pdf_file.filename.lower().endswith('.pdf'):
#         raise HTTPException(status_code=400,detail="Only pdf files are allowed")
#     if not content:
#         raise HTTPException(status_code=400,detail="Uploaded PDF is empty")
    
#     #hash the file
#     file_hash = hashlib.sha256(content).hexdigest()

#     #get user_id
#     user_data = supabase_client.table("pdf_user").select("id").eq("email", user_email).execute()
#     if not user_data.data:
#         raise HTTPException(status_code=404, detail="User not found")
#     user_id = user_data.data[0]["id"]

#     #check for duplicate files
#     hash_check = supabase_client.table("user_pdfs").select("id").eq("file_hash", file_hash).execute()
#     if hash_check.data:
#         raise HTTPException(status_code=400, detail="File already exists")
    
#     #check PDF limit(5 per user)
#     pdf_count = supabase_client.table("user_pdfs").select("id", count="exact").eq("user_id",user_id).execute()
#     count = pdf_count.count if hasattr(pdf_count, 'count') else len(pdf_count.data)
#     if count>=5:
#         raise HTTPException(status_code=400,detail="Maximum 5 pdfs per user reached")
    
#     #upload to storage supabase
#     file_path = f"{user_id}/{pdf_file.filename}"
#     try:
#         response = supabase_client.storage.from_("pdf-upload").upload(
#             file_path,content, file_options={"content_type":"application/pdf"}
#             )
#         if hasattr(response, 'error') and response.error:
#             raise HTTPException(status_code=500, detail=f"File upload failed: {response.error}")
        
#         #generate public url
#         pdf_url = f"{SUPASBASE_STORAGE_ENDPOINT}/pdf-upload/{file_path}"       

#         #save metadata
#         pdf_data = {
#             "user_id":user_id,
#             "file_name":pdf_file.filename,
#             "pdf_url":pdf_url,
#             "file_hash":file_hash,
#             "full_text": full_text,
#             "summary": summary
#         } 
#         insert_response = supabase_client.table("user_pdfs").insert(pdf_data).execute()
#         if not insert_response.data:
#             # Rollback upload
#             supabase_client.storage.from_("pdf-upload").remove([file_path])
#             raise HTTPException(status_code=500, detail="Failed to save pdf metadata")
#         return {
#             "message":"File uploaded successfully",
#             "file_name": pdf_file.filename,
#             "pdf_url":pdf_url
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Upload failed : {str(e)}")
#     finally:
#         await pdf_file.close()


async def upload_pdf_to_storage(pdf_file: UploadFile, content: bytes, user_email: str, full_text: str, summary: str) -> dict:
    if not pdf_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

    # Sanitize file name
    sanitized_filename = re.sub(r'[^\w\-\.]', '_', pdf_file.filename).lower()
    file_hash = hashlib.sha256(content).hexdigest()
    logger.debug(f"Sanitized filename: {sanitized_filename}, Hash: {file_hash}")

    # Get user_id
    user_data = supabase_client.table("pdf_user").select("id").eq("email", user_email).execute()
    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = str(user_data.data[0]["id"])

    # Check for duplicate files
    hash_check = supabase_client.table("user_pdfs").select("id").eq("file_hash", file_hash).execute()
    if hash_check.data:
        raise HTTPException(status_code=400, detail="File already exists")

    # Check PDF limit (5 per user)
    pdf_count = supabase_client.table("user_pdfs").select("id", count="exact").eq("user_id", user_id).execute()
    count = pdf_count.count if hasattr(pdf_count, 'count') else len(pdf_count.data)
    if count >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 PDFs per user reached")

    # Upload to Supabase storage
    encoded_filename = quote(sanitized_filename)  # Encode for URL safety
    file_path = f"{user_id}/{encoded_filename}"
    logger.info(f"Uploading file {sanitized_filename} to path {file_path} for user {user_email}")
    try:
        response = supabase_client.storage.from_("pdf-upload").upload(
            file_path, content, file_options={"content-type": "application/pdf"}
        )
        if hasattr(response, 'error') and response.error:
            raise HTTPException(status_code=500, detail=f"File upload failed: {response.error}")

        # Verify upload
        list_response = supabase_client.storage.from_("pdf-upload").list(path=user_id)
        uploaded_files = [f["name"] for f in list_response if isinstance(f, dict) and "name" in f]
        if sanitized_filename not in uploaded_files and unquote(encoded_filename) not in uploaded_files:
            logger.error(f"File {file_path} not found in storage after upload")
            supabase_client.storage.from_("pdf-upload").remove([file_path])
            raise HTTPException(status_code=500, detail="File upload verification failed")
        
        # Generate public URL
        pdf_url = f"{SUPABASE_STORAGE_ENDPOINT}/pdf-upload/{file_path}"

        # Save metadata
        pdf_data = {
            "user_id": user_id,
            "file_name": sanitized_filename,  # Store sanitized name
            "pdf_url": pdf_url,
            "file_hash": file_hash,
            "full_text": full_text,
            "summary": summary
        }
        insert_response = supabase_client.table("user_pdfs").insert(pdf_data).execute()
        if not insert_response.data:
            # Rollback upload
            supabase_client.storage.from_("pdf-upload").remove([file_path])
            raise HTTPException(status_code=500, detail="Failed to save PDF metadata")
        return {
            "message": "File uploaded successfully",
            "file_name": sanitized_filename,
            "pdf_url": pdf_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        await pdf_file.close()

'''
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
    from urllib.parse import quote
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    file_path = f"{user_id}/{quote(file_name)}"
    #file_path = f"{user_id}/{file_name}"
    print(f"File path: {file_path} for user: {user_email}")
    logger.info(f"Deleting file {file_name} with path {file_path} for user {user_email}")

    try:
        response = supabase_client.storage.from_("pdf-upload").remove([file_path])
        logger.info(f"Delete response: {response}")

        #verify if deletion was successful
        list_response = supabase_client.storage.from_("pdf-upload").list(path=user_id)
        remaining_files = [file.name for file in list_response.data if file.name == file_name]
        encoded_file_name = quote(file_name)
        if file_name in remaining_files or encoded_file_name in remaining_files:
            logger.error(f"File {file_name} deletion failed, still exists in storage")
            raise HTTPException(status_code=500, detail=f"File {file_name} deletion failed, still exists in storage")

        # if hasattr(response, 'error') and response.error:
        #     raise HTTPException(status_code=500, detail=f"File deletion failed {response.error}")
        
        supabase_client.table("user_pdfs").delete().eq("id",pdf_id).execute()
        logger.info(f"Successfully deleted PDF {pdf_id} and file {file_path}")
        return {"message":f"File {file_name} delete successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
'''

async def delete_pdf_from_storage(pdf_id: int, user_email: str) -> dict:
    logger.info(f"Starting deletion for PDF ID: {pdf_id}, User: {user_email}")

    # Get user data
    user_data = supabase_client.table("pdf_user").select("id").eq("email", user_email).execute()
    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = user_data.data[0]["id"]
    logger.debug(f"User ID: {user_id}, Email: {user_email}")

    # Get pdf data - check here the id
    pdf_data = supabase_client.table("user_pdfs").select("file_name, user_id").eq("id", pdf_id).execute()
    if not pdf_data.data:
        raise HTTPException(status_code=404, detail="PDF not found")
    if pdf_data.data[0]["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this PDF")
    file_name = pdf_data.data[0]["file_name"]
    logger.debug(f"PDF ID: {pdf_id}, File name: {file_name}")

    # Construct file path
    # file_path = f"{user_id}/{file_name}"  # Use raw file_name as stored
    # encoded_file_path = f"{user_id}/{quote(file_name)}"  # Encoded for API
    file_paths = [
        f"{user_id}/{file_name}",                    # As stored (e.g., medical_record-colon.pdf)
        f"{user_id}/{quote(file_name)}",             # Encoded (e.g., medical_record%2Dcolon.pdf)
        f"{user_id}/{file_name.replace('_', '-')}",  # Alternative separator (e.g., medical-record-colon.pdf)
        f"{user_id}/{quote(file_name.replace('_', '-'))}"  # Encoded alternative
    ]
    logger.info(f"Attempting to delete files: {file_paths} for user: {user_email}")

    deleted = False
    for file_path in file_paths:
        logger.info(f"Trying to delete file: {file_path}")
        try:
            response = supabase_client.storage.from_("pdf-upload").remove([file_path])
            logger.info(f"Storage delete response for {file_path}: {response}")

            # Verify file is deleted
            list_response = supabase_client.storage.from_("pdf-upload").list(path=user_id)
            logger.debug(f"List response: {list_response}")
            remaining_files = [f["name"] for f in list_response if isinstance(f, dict) and "name" in f]
            logger.debug(f"Remaining files in {user_id}/: {remaining_files}")

            file_variations= [
                file_name,  # Original name
                unquote(file_name),  # URL-decoded name
                quote(file_name),  # URL-encoded name
                file_name.replace('_', '-'),  # Alternative separator
                quote(file_name.replace('_', '-'))  # URL-encoded alternative
            ]
            if any(variation in remaining_files for variation in file_variations):
                logger.error(f"File {file_path} deletion failed, still exists in storage")
                continue
            deleted = True
            break  # Exit loop if deletion was successful

        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            continue  # Try next file path variation
    if not deleted:
        logger.error(f"Failed to delete any variations of file {file_name} for user {user_email}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file {file_name} from storage")

    try:
        # Delete from database
        delete_response = supabase_client.table("user_pdfs").delete().eq("id", pdf_id).execute()
        if not delete_response.data:
            logger.error(f"Failed to delete PDF {pdf_id} from user_pdfs table")
            raise HTTPException(status_code=500, detail="Failed to delete PDF metadata")
        logger.info(f"Successfully deleted PDF {pdf_id} with file {file_path}")

    except Exception as e:
        logger.error(f"Deletion failed for PDF {pdf_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete: {str(e)}")
    return {"message": f"File {file_name} deleted successfully"}


async def get_user_pdfs(user_email:str)->list:
    # get list of user pdfs
    user_data = supabase_client.table("pdf_user").select("id").eq("email",user_email).execute()
    if not user_data.data:
        raise HTTPException(status_code=404,detail="User not found")
    user_id = user_data.data[0]["id"]

    pdfs = supabase_client.table("user_pdfs"
                        ).select("id, file_name,pdf_url,created_at").eq("user_id",user_id).order("created_at",desc=True).execute()
    return pdfs.data or []



