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


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 3600

"johndoe, admin"


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="log")

router = APIRouter(prefix="/auth")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)



def get_user( username: str):
    with Session(engine) as session:
        db = select(Admin).where(Admin.user_name == username)
        user = session.scalar(db)
        if user:
            print(user)
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
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
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

@router.get("/log", response_class=HTMLResponse)
def log_on(request: Request):
    
    if request.cookies.get("access_token"):
        return RedirectResponse("/admin-page", 302)
    

    return templates.TemplateResponse("auth/login.html",{"request": request})

@router.post("/log")
async def log_on(form_data: Annotated[OAuth2PasswordRequestForm,Depends()])->Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = create_access_token(data={"sub": user.user_name})
    
    response = RedirectResponse("/admin-page",302)
    response.set_cookie(key = "access_token",value= token, expires=ACCESS_TOKEN_EXPIRE_MINUTES,httponly=True,secure=True,samesite="lax")
    return response
    


@router.get("/logout", response_class=HTMLResponse)
def logout(request : Request):
    response = RedirectResponse("/",302)
    response.delete_cookie(key="access_token")
    return response
    