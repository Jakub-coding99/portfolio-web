from fastapi import  HTTPException,Request
import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
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
        

    


    