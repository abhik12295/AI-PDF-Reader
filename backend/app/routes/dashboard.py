# from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
# from fastapi.responses import HTMLResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from pathlib import Path
# from dotenv import load_dotenv
# from backend.app.db.supabase import supabase_client, SUPABASE_BUCKET , SUPABASE_URL
# from ..auth_config import get_current_user
# from backend.app.services.file_service import extract_pdf_text, get_summary, upload_pdf_to_storage,delete_pdf_from_storage,get_user_pdfs
# import os
# import jwt

# router = APIRouter()

# BASE_DIR = Path(r"C:\Users\stuar\Desktop\AI PDF fastapi")
# templates = Jinja2Templates(directory=BASE_DIR / "frontend/templates")

# #with authentication
# @router.get("/", response_class=HTMLResponse)
# async def dashboard_page(request: Request, current_user: dict = Depends(get_current_user)):
#     try:
#         pdfs = await get_user_pdfs(current_user["email"])
#         return templates.TemplateResponse("dashboard.html", {
#             "request": request,
#             "user": current_user,
#             "pdfs":pdfs
#         })
#     except Exception as e:
#         return templates.TemplateResponse("dashboard.html", {
#             "request": request,
#             "user": current_user,
#             "error": str(e),
#             "pdfs": []
#         })

# # @router.post("/dashboard", response_class=HTMLResponse)
# # async def dashboard(
# #     request:Request,
# #     pdf: UploadFile = File(...),
# #     current_user: dict = Depends(get_current_user)
# # ):
# #     print(f"Authenticated User: {current_user}")
# #     print(f"PDF Parameter type: {type(pdf)}")
# #     print(f"PDF Parameter type: {pdf}")
# #     print(f"PDF filename: {pdf.filename if hasattr(pdf,'filename') else 'N/A'}")
# #     if not current_user:
# #         raise HTTPException(status_code=401, detail="Unauthorized")
# #     try:
# #         pdf_text = await extract_pdf_text(pdf)
# #         summary = get_summary(pdf_text)
# #         return templates.TemplateResponse("dashboard.html",{
# #             "request":request,  
# #             "full_text": pdf_text,
# #             "summary":summary,
# #             "user":current_user
# #         })
    
# #     except Exception as e:
# #         return templates.TemplateResponse("dashboard.html",{
# #             "request":request,
# #             "error":str(e),
# #             "user":current_user
# #         })

# @router.post("/upload", response_class=HTMLResponse)
# async def upload_pdf(
#     request: Request,
#     pdf: UploadFile = File(...),
#     current_user: dict = Depends(get_current_user)
# ):
#     print(f"authenticated user: {current_user}")
#     print(f"PDF Parameter type: {type(pdf)}")
#     print(f"PDF Parameter Content: {pdf}")
#     print(f"PDF Filename: {pdf.filename if hasattr(pdf, 'filename') else 'N/A'}")

#     try:
#         content = await pdf.read()
#         if not content:
#             raise HTTPException(status_code=400, detail="Upload file is empty")
        
#         #upload to storage
#         upload_result = await upload_pdf_to_storage(pdf, content, current_user["email"])

#         #extract text and summarize
#         pdf_text = await extract_pdf_text(content,pdf.filename)
#         summary = get_summary(pdf_text)

#         pdfs = await get_user_pdfs(current_user["email"])
#         return templates.TemplateResponse("dashboard.html",{
#             "request":request,
#             "full_text":pdf_text,
#             "summary":summary,
#             "user":current_user,
#             "pdfs":pdfs,
#             "message":upload_result["message"]
#         })
    
#     except Exception as e:
#         print(f"Error in upload: {str(e)}")
#         pdfs = await get_user_pdfs(current_user["email"])
#         return templates.TemplateResponse("dashboard.html",{
#             "request":request,
#             "error":str(e),
#             "user":current_user,
#             "pdfs":pdfs
#         })
#     finally:
#         await pdf.close()
    
# @router.post("/delete/{pdf_id}", response_class=HTMLResponse)
# async def delete_pdf(
#     request:Request,
#     pdf_id: int,
#     current_user:dict = Depends(get_current_user)
# ):
#     try:
#         delete_result = await delete_pdf_from_storage(pdf_id, current_user["email"])
#         pdfs = await get_user_pdfs(current_user["email"])
#         return RedirectResponse("/dashboard", status_code=303)
#         # return templates.TemplateResponse("dashboard.html",{
#         #     "request":request,
#         #     "user":current_user,
#         #     "pdfs":pdfs,
#         #     "message":delete_result["message"]
#         # })
#     except Exception as e:
#         print(f"Error in delete: {str(e)}")
#         pdfs = await get_user_pdfs(current_user["email"])
#         return templates.TemplateResponse("dashboard.html",{
#             "request":request,
#             "error":str(e),
#             "user":current_user,
#             "pdfs":pdfs
#         })


#above code is running fine
# also below code is running fine

from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import load_dotenv
from backend.app.db.supabase import supabase_client, SUPABASE_BUCKET, SUPABASE_URL
from ..auth_config import get_current_user
from backend.app.services.file_service import extract_pdf_text, get_summary, upload_pdf_to_storage, delete_pdf_from_storage, get_user_pdfs, ask_question_about_summary
import os
import jwt
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

BASE_DIR = Path(r"C:\Users\stuar\Desktop\AI PDF fastapi")
templates = Jinja2Templates(directory=BASE_DIR / "frontend/templates")

# With authentication
@router.get("/", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        pdfs = await get_user_pdfs(current_user["email"])
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": current_user,
            "pdfs": pdfs,
            "chat_messages": []  # Initialize empty chat list
        })
    except Exception as e:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": current_user,
            "error": str(e),
            "pdfs": [],
            "chat_messages": []
        })

@router.post("/upload", response_class=HTMLResponse)
async def upload_pdf(
    request: Request,
    pdf: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    print(f"authenticated user: {current_user}")
    print(f"PDF Parameter type: {type(pdf)}")
    print(f"PDF Parameter Content: {pdf}")
    print(f"PDF Filename: {pdf.filename if hasattr(pdf, 'filename') else 'N/A'}")

    try:
        content = await pdf.read()
        if not content:
            raise HTTPException(status_code=400, detail="Upload file is empty")
        
        # Extract text and summarize
        pdf_text = await extract_pdf_text(content, pdf.filename)
        summary = get_summary(pdf_text)
        # Upload to storage
        upload_result = await upload_pdf_to_storage(pdf, content, current_user["email"], pdf_text, summary)

        pdfs = await get_user_pdfs(current_user["email"])
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "full_text": pdf_text,
            "summary": summary,
            "user": current_user,
            "pdfs": pdfs,
            "message": upload_result["message"],
            "chat_messages": []  # Reset chat list on upload
        })
    
    except Exception as e:
        print(f"Error in upload: {str(e)}")
        pdfs = await get_user_pdfs(current_user["email"])
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "error": str(e),
            "user": current_user,
            "pdfs": pdfs,
            "chat_messages": []
        })
    finally:
        await pdf.close()

'''
@router.post("/delete/{pdf_id}", response_class=HTMLResponse)
async def delete_pdf(
    request: Request,
    pdf_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        delete_result = await delete_pdf_from_storage(pdf_id, current_user["email"])
        pdfs = await get_user_pdfs(current_user["email"])
        return RedirectResponse("/dashboard", status_code=303)
    except Exception as e:
        print(f"Error in delete: {str(e)}")
        pdfs = await get_user_pdfs(current_user["email"])
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "error": str(e),
            "user": current_user,
            "pdfs": pdfs,
            "chat_messages": []
        })
'''


@router.post("/delete/{pdf_id}", response_class=HTMLResponse)
async def delete_pdf(
    request: Request,
    pdf_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        delete_result = await delete_pdf_from_storage(pdf_id, current_user["email"])
        pdfs = await get_user_pdfs(current_user["email"])
        return RedirectResponse(url="/dashboard?message=PDF+deleted+successfully", status_code=303)
    except HTTPException as e:
        logger.error(f"Delete failed for PDF {pdf_id}: {str(e)}")
        error_message = str(e.detail).replace(' ', '+')
        return RedirectResponse(url=f"/dashboard?error={error_message}", status_code=303)
    except Exception as e:
        logger.error(f"Unexpected error deleting PDF {pdf_id}: {str(e)}")
        error_message = str(e).replace(' ', '+')
        return RedirectResponse(url=f"/dashboard?error=Unexpected+error:+{error_message}", status_code=303)

@router.post("/ask", response_class=JSONResponse)
async def ask_question(
    request: Request,   
    current_user: dict = Depends(get_current_user)
):
    if not current_user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    
    try:
        form_data = await request.form()
        question = form_data.get("question")
        summary = form_data.get("summary")
        if not question or not summary:
            return JSONResponse({"error": "Question and summary are required"}, status_code=400)
        
        answer = ask_question_about_summary(summary, question)
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    


