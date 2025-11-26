from fastapi import  HTTPException,Request
import jwt
from dotenv import find_dotenv,load_dotenv
import os 


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"




def get_current_user_from_cookies(request : Request):
    token = request.cookies.get("access_token")
   
    

    if not token:
        raise HTTPException(status_code=401,detail="Not authenticated!")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if not user:
            raise HTTPException(status_code=401,detail="Invalid token!")
        return user
    
    except jwt.PyJWTError:
        raise HTTPException(status_code=401,detail= "Invalid token!")
        

    


    