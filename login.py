from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi.requests import Request
from fastapi.responses import HTMLResponse,RedirectResponse
import jwt
from fastapi import Depends, FastAPI, HTTPException, status,Form,requests,Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from database import Admin

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30






class UserLog(BaseModel):
    username : str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="log")

app = FastAPI()


app.mount("/static",StaticFiles(directory="static"),name="static")
templates = Jinja2Templates(directory="auth/templates")



@app.get("/",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("auth/index.html",{"request":request})


@app.post("/test_url",response_class=HTMLResponse)
async def js_test(request:Request):
    data = await request.json()
    print(data)

def token_to_js(token):
    return token

@app.post("/new_token" ,response_class=HTMLResponse)
def send_token(request:Request):
    new_token = token_to_js()
    print(new_token + "nový")
    return new_token




def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)





def authenticate_user(fake_db, username: str, password: str):
                    

    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
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
    print("token:" + encoded_jwt)

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
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get("/log", response_class=HTMLResponse)
def log_on(request: Request):
    return templates.TemplateResponse("login.html",{"request": request})

@app.post("/log")
async def log_on(form_data: Annotated[OAuth2PasswordRequestForm,Depends()])->Token:
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
   
    # access_token = create_access_token(
    #     data={"sub": user.username}, expires_delta=access_token_expires
    token = create_access_token(data={"sub": user.username})

    response = RedirectResponse("/dashboard",302)
    response.set_cookie(key = "access_token",value= token, expires=ACCESS_TOKEN_EXPIRE_MINUTES,httponly=True,secure=True,samesite="lax")
    return response
    
@app.get("/dashboard",response_class=HTMLResponse)
def dash(request:Request):
    token = request.cookies.get("access_token")
    
    if not token:
        return RedirectResponse("/log",302)
       
    try:
        
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get("sub")
    except:
   
        return RedirectResponse("/log",302)
    
    return templates.TemplateResponse("dashboard.html", {"request":request,"username":username})

@app.get("/logout", response_class=HTMLResponse)
def logout(request : Request):
    response = RedirectResponse("/log",302)
    response.delete_cookie(key="access_token")
    return response
    