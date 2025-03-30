from fastapi import HTTPException, Response
from backend.app.db.supabase import supabase_client
from starlette.responses import Response, RedirectResponse

def register_user(email: str, password: str):
    try:
        response = supabase_client.auth.sign_up({
            "email": email, "password": password
            })
        print("Supabase Response:", response)  # Add this for debugging
        if response.user is None:
            raise HTTPException(status_code=400, detail='Signup Failed')
        return RedirectResponse('/login', status_code=303)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # if response.get("error"):
    #     raise HTTPException(status_code=400, detail="User already exists or invalid data")
    # return {"message": "User registered successfully, check your email for confirmation"}

def login_user(email: str, password: str, response: Response):
    try:
        auth_response = supabase_client.auth.sign_in_with_password({
            "email": email, "password": password
            })
        if auth_response.user is None:
            raise HTTPException(status_code=400, detail='Login Failed')
        access_token = auth_response.session.access_token
        response = RedirectResponse('/', status_code=303)
        response.set_cookie(key = 'access_token', value=f"Bearer {access_token}", httponly=True)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
        #if "error" in auth_response and auth_response["error"]:
        #    raise HTTPException(status_code=400, detail=auth_response["error"]["message"])

        #session_data = auth_response.get("session")
        #if not session_data:
        #    raise HTTPException(status_code=400, detail="Authentication failed")

        ## Set HTTP-only cookies for session management
        #response.set_cookie("access_token", session_data["access_token"], httponly=True, samesite="Lax")
        #response.set_cookie("refresh_token", session_data["refresh_token"], httponly=True, samesite="Lax")

    #     #return {"message": "Login successful"}

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


def logout_user(response: Response):
    response = RedirectResponse('/login', status_code=303)
    response.delete_cookie(key = "access_token")
    #response.delete_cookie("refresh_token")
    return response

