from fastapi import APIRouter, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import load_dotenv
from backend.app.db.supabase import supabase_client, SUPABASE_BUCKET , SUPABASE_URL
from ..auth_config import get_current_user


router = APIRouter()

# Path to the base directory (adjusted to ensure the correct path)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# JWT_KEY = os.getenv("JWT_KEY")

# def verify_token(request: Request):
#     token = request.cookies.get(key = "access_token")
#     if not token:
#         raise HTTPException(status_code=401, detail="Missing access token")

#     try:
#         payload = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
#         return payload  # Return user details
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Access token expired")
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


templates = Jinja2Templates(directory=BASE_DIR / "frontend/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request:Request,user_data: dict = Depends(get_current_user), pdf: UploadFile = File(None)):
    pdf_url = None
    if pdf and pdf.filename!= "":
        pdf_fileName = f"{user_data}.id_{pdf.filename}"
        file_content = await pdf.read()
        response = supabase_client.storage.from_(SUPABASE_BUCKET).upload(pdf_fileName, file_content)
        if response.status_code == 200:
            pdf_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{pdf_fileName}"
        
        supabase_client.table('user_pdf').insert({
            'first_name': None,
            'last_name': None,
            'email': user_data.email,
            'pdf_url': pdf_url
        }).execute()
    
    
    #return RedirecrResponse("/", status_code = 300)
    return templates.TemplateResponse("dashboard.html")

    #return {"message": "Welcome to the dashboard!", "user": user_data}
