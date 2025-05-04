from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from backend.app.db.supabase import JWT_KEY

print(f"JWT_KEY: {JWT_KEY}")

#JWT config
security = HTTPBearer()


# async def auth_middleware(request: Request, call_next):
#     token = request.cookies.get('access_token')
#     print(f"Middleware - Path: {request.url.path}")
#     print(f"Middleware - access_token cookie: {token}")
#     if token:
#         # Remove surrounding quotes and handle "Bearer " prefix
#         clean_token = token.strip('"')
#         print(f"Middleware - Cleaned token: {clean_token}")
#         if clean_token.startswith('Bearer '):
#             extracted_token = clean_token.split(' ', 1)[1]
#             print(f"Middleware - Extracted token: {extracted_token}")
#             request.headers.__dict__['_list'].append(
#                 (b"authorization", f"Bearer {extracted_token}".encode())
#             )
#         else:
#             print("Middleware - Token does not start with 'Bearer '")
#     else:
#         print("Middleware - No token found")
#     response = await call_next(request)
#     return response

async def auth_middleware(request: Request, call_next):
    print(f"Middleware - Path: {request.url.path}, Method: {request.method}")
    token = request.cookies.get('access_token')
    print(f"Middleware - access_token cookie: {token}")
    if token:
        clean_token = token.strip('"')
        print(f"Middleware - Cleaned token: {clean_token}")
        extracted_token = clean_token.replace('Bearer ', '') if clean_token.startswith('Bearer ') else clean_token
        print(f"Middleware - Extracted token: {extracted_token}")
        new_headers = dict(request.headers)
        new_headers['authorization'] = f"Bearer {extracted_token}"
        request.scope['headers'] = [
            (k.encode('utf-8'), v.encode('utf-8')) for k, v in new_headers.items()
        ]
        #request._headers = new_headers
        print(f"Middleware - Added Authorization header: {new_headers['authorization']}")
        print(f"Middleware - All headers: {new_headers}")
    else:
        print("Middleware - No token found")
    response = await call_next(request)
    return response


#def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # try:
    #     token = credentials.credentials
    #     if token.startswith('Bearer '):
    #         token = token.split(' ')[1]
    #     payload = jwt.decode(token, JWT_KEY, algorithms=['HS256'], options={'verify':False})
        
    #     user_id = payload.get('sub')
    #     if user_id is None:
    #         raise HTTPBearer(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Invalid auth creds')
    #     return payload
    # except jwt.ExpiredSignatureError:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has expired')
    # except jwt.PyJWKError as e:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        print(f"get_current_user - Raw credentials: {token}")
        clean_token = token.strip()
        #clean_token = token.replace("Bearer ", "").strip() if token.startswith("Bearer ") else token
        print(f"get_current_user - Extracted token: {clean_token}")
        payload = jwt.decode(
            clean_token,
            JWT_KEY,
            algorithms=['HS256'],
            options={
                'verify_signature': False,
                'verify_aud': False,
                'verify_exp': False
            }
        )
        print(f"get_current_user - Payload: {payload}")
        user_id = payload.get('sub') or payload.get('user_id')
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid auth creds')
        return payload
    except jwt.PyJWTError as e:
        print(f"get_current_user - JWT Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate user: {str(e)}')
    except Exception as e:
        print(f"get_current_user - Unexpected Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')