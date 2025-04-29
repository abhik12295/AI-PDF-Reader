from fastapi import APIRouter, Depends, Response, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from backend.app.db.supabase import JWT_KEY

#JWT config
security = HTTPBearer()

async def auth_middleware(request: Request, call_next):
    token = request.cookies.get('access_token')
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1]
        request.headers.__dict__['list'].append(
            (b"authorization", f"Bearer {token}".encode())
        )
    response = await call_next(request)
    return response

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        if token.startswith('Bearer '):
            token = token.split(' ')[1]
        payload = jwt.decode(token, JWT_KEY, algorithms=['HS256'], options={'verify':False})
        
        user_id = payload.get('sub')
        if user_id is None:
            raise HTTPBearer(status_code = status.HTTP_401_UNAUTHORIZED, detail = 'Invalid auth creds')
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token has expired')
    except jwt.PyJWKError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
        
