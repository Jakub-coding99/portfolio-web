from fastapi import FastAPI,Request,Depends ,File, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
import secrets
from database import Projects, Admin,create_db_and_tables,engine

import os

from sqlmodel import Session,select
from typing import List


app = FastAPI()

security = HTTPBasic()

create_db_and_tables()


@app.post("/test",response_class = HTMLResponse)
async def  test(request : Request,title:str = Form(...),popis:str = Form(...),files: List[UploadFile] = Form(...)):
    img_path = []
    
    for file in files:
        UPLOAD_DIR = "static/img/"
        os.makedirs(UPLOAD_DIR,exist_ok=True)
        location_file = os.path.join(UPLOAD_DIR,file.filename)
    
        with open (location_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        img_path.append(location_file)
    print(img_path)
    
    new_project = Projects(title=title,description=popis,image_url=img_path)
    with Session(engine) as session:
        session.add(new_project)
        session.commit()
    
        # project = session.get(Projects, 2) 
        # print(project.description)
   
       
    return templates.TemplateResponse("test.html", {"request":request,"filename": [f.filename for f in files]})

@app.get("/test", response_class=HTMLResponse)
def get_test(request : Request):
     return templates.TemplateResponse("test.html", {"request":request})




@app.get("/user/admin")
def admin(credentials : Annotated[HTTPBasicCredentials,Depends(security)]):
        return {"username": credentials.username, "password": credentials.password}








projects = [{"id" : 1,"title":"TicTacToe","description" : "Muj první projekt" },{"id" : 2}, {"id" : 3} ]


app.mount("/static",StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request : Request):
    return templates.TemplateResponse("index.html",{"request":request, "projects" : projects})


@app.get("/projects/{id}",response_class=HTMLResponse)
def get_project(request : Request ,id : int):
    
    for p in projects:
        if p["id"] == id:
            project = p
           
            break

    if project is None:
        return HTMLResponse("<p>chyba</p>",status_code=404)
    return templates.TemplateResponse("projects.html", {"request":request, "project" : project})
    

@app.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request":request})
    