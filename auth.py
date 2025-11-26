from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.requests import Request
from fastapi.responses import HTMLResponse,RedirectResponse
import jwt
from fastapi import Depends, HTTPException, status,APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from database import Admin,Session,select,engine
from core.templates import templates
import os
from dotenv import load_dotenv,find_dotenv


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)



SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600
LOGIN_URL = os.getenv("LOGIN_URL")
ADMIN_URL = os.getenv("ADMIN_PAGE_URL")
TOKEN_URL = os.getenv("TOKEN_URL")
LOGOUT_URL = os.getenv("LOGOUT_URL")
PREFIX = os.getenv("PREFIX")




class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)

router = APIRouter(prefix=PREFIX)


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)



def get_user( username: str):
    with Session(engine) as session:
        db = select(Admin).where(Admin.user_name == username)
        user = session.scalar(db)
        if user:
            
            return user
    


def authenticate_user( username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
   
    return user

def auth_from_cookie(request:Request):
    token = request.cookies.get("access_token")
    if not token:
        return
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
        username = payload.get("sub")
        if not username:
            return None
        return get_user(username)
    except:
        return None



@router.get(LOGIN_URL, response_class=HTMLResponse)
async def log_on(request: Request):
    user = auth_from_cookie(request)
    if not user:
        return templates.TemplateResponse("auth/login.html",{"request": request})
    else:
        
        return RedirectResponse(ADMIN_URL, 302)
      


    

@router.post(LOGIN_URL)
async def log_on(form_data: Annotated[OAuth2PasswordRequestForm,Depends()])->Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(data={"sub": user.user_name})
    
    response = RedirectResponse(ADMIN_URL,302)
    response.set_cookie(key = "access_token",value= token, expires=ACCESS_TOKEN_EXPIRE_MINUTES,httponly=True,secure=True,samesite="lax")
    return response
    


@router.get(LOGOUT_URL, response_class=HTMLResponse)
def logout(request : Request):
    response = RedirectResponse("/",302)
    response.delete_cookie(key="access_token")
    return response
    