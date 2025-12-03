from fastapi import FastAPI,Request,Depends ,File, Form, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse,JSONResponse
from database import Projects,Blog,create_db_and_tables,engine,Session,select,Admin
import os
from typing import List, Optional
from fastapi.responses import RedirectResponse
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from dotenv import load_dotenv,find_dotenv
import markdown
from auth import router as auth_router
from core.templates import templates
from core.security import get_current_user_from_cookies
from urllib.parse import unquote
import shutil

#TEST IF DISK WORKS

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


ADD_PROJECT_URL = os.getenv("ADD_PROJECT_URL")
ADMIN_PAGE_URL =  os.getenv("ADMIN_PAGE_URL")
ADMIN_EDIT_PROJECT = os.getenv("ADMIN_EDIT_PROJECT")
LOGIN_URL = os.getenv("LOGIN_URL")
PREFIX = os.getenv("PREFIX")
DELETE_CONTENT_URL = os.getenv("DELETE_CONTENT_URL")
DELETE_IMG = os.getenv("DELETE_IMG")


MODEL = {
    "project": {
        "model" : Projects,
        "template_edit" : "admin/edit_content.html",
        "template_add" : "admin/add_project.html",
        "redirect" : ADMIN_PAGE_URL,
        "model_type" : "project"
        

    },
    "blog": {
        "model":Blog,
        "template_edit": "admin/edit_content.html",
        "model_type" : "blog"


    }
}


app = FastAPI()

app.include_router(auth_router)



PERSISTENT_DIR = "/mnt/data"

RENDER_DISC = os.path.join(PERSISTENT_DIR,"media","photos")

os.makedirs(RENDER_DISC,exist_ok=True)

app.mount("/media",StaticFiles(directory=os.path.join(PERSISTENT_DIR,"media")), name="media")

app.mount("/static",StaticFiles(directory="static"), name="static")


create_db_and_tables()

def set_admin():
    from pwdlib import PasswordHash
    password_hash = PasswordHash.recommended()
   

    with Session(engine) as session:
        admin = session.scalars(select(Admin)).first()
        if admin:
            return
        else:
            hashed_pass = password_hash.hash(os.getenv("password"))
            new_admin = Admin(user_name=os.getenv("user_name"), password=hashed_pass)
            session.add(new_admin)
            session.commit()
            

           

set_admin()


@app.exception_handler(HTTPException)
async def custom_exception(request:Request, exc:HTTPException):
    if exc.status_code == 401:
        return RedirectResponse(f"{PREFIX}{LOGIN_URL}", 302)
    raise exc


@app.get("/add-new",response_class = HTMLResponse)
def add_content(request : Request,admin=Depends(get_current_user_from_cookies),model_type= str):
    return templates.TemplateResponse("admin/add_content.html",{"request":request,"api_url" : ADD_PROJECT_URL})



@app.post(ADD_PROJECT_URL,response_class = HTMLResponse,)
async def add_project(request : Request,title:str = Form(...),description:str = Form(...),
                      files: List[UploadFile] = File(None),
                      preview:Optional[str] = Form(None),admin=Depends(get_current_user_from_cookies),model_type= str):
    
    config= MODEL.get(model_type)
    model = config["model"]
    img_path = []
    
    empty_data = all(len(x) == 0  for x in (title,description,preview))
    
    if empty_data == True and files == None:
        return JSONResponse({"redirect": ADMIN_PAGE_URL})
    
    if files == None:
        fallback_img = "media/photos/no-img.png"
        
        if os.path.exists(fallback_img):
            img_path.append(fallback_img)
           
        else:

            target_dir = "media/photos/"
            os.makedirs(target_dir, exist_ok=True) 
            source = "static/my-img/no-img.png"
            destination = os.path.join(target_dir, "no-img.png")
            shutil.copy2(source, destination)
            img_path.append(destination)
        
            
    else:
        await upload_img(files,None,img_path)

       
    
    html_text = markdown.markdown(description)
    markdown_text = description
    
    if preview == None:
        preview = ""
    
    new_model = model(title=title, description=html_text,image_url=img_path,preview=preview,markdown=markdown_text)
    with Session(engine) as session:
        
        session.add(new_model)
        session.commit()
    
    return JSONResponse({"redirect": ADMIN_PAGE_URL})

   

@app.get(ADMIN_PAGE_URL, response_class=HTMLResponse)
def get_admin_pannel(request : Request,admin=Depends(get_current_user_from_cookies)):
    projects = all_project()
    posts = blog_posts()
    return templates.TemplateResponse("admin/admin_main.html", {"request":request,"projects":projects,"posts":posts})


@app.get(DELETE_CONTENT_URL,response_class=HTMLResponse)
def delete_project(request:Request,id : int, model_type = str,admin = Depends(get_current_user_from_cookies)):
    config = MODEL.get(model_type)
    model = config["model"]
    
    with Session(engine) as session:
        app_path = os.path.dirname(os.path.abspath(__file__))
        choosen_model = session.get(model,id)
        if choosen_model:
            for img in choosen_model.image_url:
                if img == "media/photos/no-img.png":
                    continue
                else:
                    try:
                        
                        to_del = f"{app_path}/{img}"
                        os.remove(to_del)
                    except (FileNotFoundError, PermissionError):
                        
                        pass

            session.delete(choosen_model)
            session.commit()

    return RedirectResponse(url=ADMIN_PAGE_URL,status_code=303)

@app.get(ADMIN_EDIT_PROJECT,response_class = HTMLResponse)
def get_edit_content(request:Request,id:int,model_type = str,admin = Depends(get_current_user_from_cookies)):

    config = MODEL.get(model_type)
    model = config["model"]
    
    
    with Session(engine) as session:
        current_img = []
        choosen_model = session.get(model,id)
        images = choosen_model.image_url
        for i in images:
            x = i.split("/")
            img = {"name":x[2],"path":i}
            current_img.append(img)
        choosen_model.image_url = current_img
        
        
    return templates.TemplateResponse(config["template_edit"],{"request":request,"project":choosen_model})


@app.post(ADMIN_EDIT_PROJECT,response_class = HTMLResponse)
async def post_edit_content(request:Request,id:int,title: str = Form(...),description:str = Form(...),preview:Optional[str] = Form(None),files: List[UploadFile] = File(None),model_type = str,admin = Depends(get_current_user_from_cookies)):
    config = MODEL.get(model_type)
    fallback_img = "media/photos/no-img.png"
    model = config["model"]
    markdown_text = description
    with Session(engine) as session:
        choosen_model = session.get(model,id)
        if not choosen_model:
            return {"eror":"not found"}
        
        if choosen_model.title != title:
           choosen_model.title = title
        
        if choosen_model.markdown != markdown_text:
            new_description = markdown.markdown(markdown_text)
            choosen_model.description = new_description
            choosen_model.markdown = markdown_text
        
        if preview is not None:
            if choosen_model.preview != preview:
                choosen_model.preview = preview
        
        try:
            await upload_img(files,choosen_model,None)
        
        except TypeError:
            pass


        
        for img in choosen_model.image_url:
            if len(choosen_model.image_url) > 1 and img == fallback_img:
                choosen_model.image_url.remove(img)

        if len(choosen_model.image_url) == 0:
            choosen_model.image_url.append(fallback_img)

        session.commit()
        return JSONResponse({"redirect": ADMIN_PAGE_URL})


async def upload_img(files,choosen_model,img_path):
    
    for file in files:
       
        DIR = "media/photos/"
        os.makedirs(DIR,exist_ok=True)
        location_file = os.path.join(DIR,file.filename)
        
        
        
       
        if choosen_model:
            choosen_model.image_url.append(location_file)
        
        if type(img_path)  == list:
            img_path.append(location_file)
            
        

        with open(location_file,"wb") as f:
            content = await file.read()
           
            f.write(content)
        






def all_project():
    projects = []
    with Session(engine) as session:
        project = select(Projects)
        all_projects = session.scalars(project).all()
       
        
        for p in all_projects:
            
            if len(p.image_url) > 0:
                preview_photo = p.image_url.copy()[0].split("/")[2]
              
            else:
                preview_photo = ""
            
           
    
            project_format = {"id" : p.id,"title":p.title.upper(),"description":p.description,"img_url":p.image_url,
                              "preview":p.preview,"markdown":p.markdown,"endpoint":p.endpoint,"preview_photo": preview_photo}
            
            projects.append(project_format)
             
    return projects


def blog_posts():
    posts = []
    with Session(engine) as session:
        blog = select(Blog)
        all_posts = session.scalars(blog).all()
        for p in all_posts:

            if len(p.image_url) > 0:
                preview_photo = p.image_url.copy()[0].split("/")[2]
            else:
                continue


            post_format = {"id" : p.id,"title":p.title.upper(),"description":p.description,"img_url":p.image_url,
                           "preview":p.preview,"markdown":p.markdown,"endpoint": p.endpoint, "preview_photo": preview_photo}
            posts.append(post_format)
    
    return posts



@app.get("/", response_class=HTMLResponse)
def home(request : Request):
    projects = all_project()
    
    return templates.TemplateResponse("index.html",{"request":request, "projects" : projects})


@app.get("/projects/{id}",response_class=HTMLResponse)
def get_project(request : Request ,id : int):
    
    all_projects = all_project()
    
    for p in all_projects:
        
        
        if p["id"] == id:
            project = p
            project_photo = [photo.split("/")[2]  for photo in project["img_url"]]
            project["img_url"] = project_photo
            break

    if project is None:
        return HTMLResponse("<p>chyba</p>",status_code=404)
    
    
    return templates.TemplateResponse("projects.html", {"request":request, "project" : project})
    

@app.post("/submit_contact",response_class=HTMLResponse)
async def contact(request:Request):
    
    
    response = await request.json()
    await send_email(response)
    return RedirectResponse(url="/#contact",status_code=303)



@app.get("/blog",response_class=HTMLResponse)
def blog(request:Request):
    posts = blog_posts()
    return templates.TemplateResponse("blog.html", {"request":request,"posts":posts})


@app.get("/blog/{id}",response_class=HTMLResponse)
def get_post(request : Request ,id : int):
    all_posts = blog_posts()

    
    for p in all_posts:
        
        if p["id"] == id:
            post = p
            break

    if p is None:
        return HTMLResponse("<p>chyba</p>",status_code=404)
    
    prev = {}
    next = {}

    index = all_posts.index(p)
    

    if len(all_posts) == 1:
        next = None
        prev = None
       


    elif index == 0:
        prev = all_posts[index + 1]
        next = None

    elif all_posts[-1] == p:
        prev = None
        next = all_posts[index - 1]
        
    

    else: 
        prev = all_posts[index + 1]
        next = all_posts[index - 1]
        

    
    


    return templates.TemplateResponse("post_template.html", {"request":request, "post" : post,"next_post":next,"prev_post":prev})
    

@app.post(DELETE_IMG,response_class=HTMLResponse)
async def check_img(request : Request):
  
    img_to_del = []
    response = await request.json()

   
    endpoint = response["endpoint"].split("/")[-2]

    with Session(engine) as session:
        if endpoint == "project":
            content = session.scalar(select(Projects).filter_by(title = response["title"]))
        else:
            content = session.scalar(select(Blog).filter_by(title = response["title"]))

        
        for x in response["images"]:
            
            decoded = unquote(x)
        
            f = decoded.split("/")
            formatted = f[5]
        

            if formatted == "no-img.png":
                continue

            for content_img in content.image_url:
                
                if formatted in content_img:
                    
                    content.image_url.remove(content_img)
                    img_to_del.append(content_img)


        session.commit()
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(BASE_DIR)
    
    for del_img in img_to_del:
        x = f"{app_path}/{del_img}"
        os.remove(x)
            
                




async def send_email(data):
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD= os.getenv("MAIL_PASSWORD"),
        MAIL_FROM= os.getenv("MAIL_FROM"),
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_SSL_TLS=False,
        MAIL_STARTTLS=True,
        )
    
    message = MessageSchema(
       subject="PORTFOLIO WEB  #PYTHON",
       recipients= ["kuba.vecera@email.cz"],
       body=f"Email z tvého webu:\n\n"
       f"JMÉNO: {data["name"]}, EMAIL: {data["email"]}\n\n"
       "ZPRÁVA:\n\n"
       f"{data["msg"]}",
       subtype="plain"
       )
    
    
    fm = FastMail(conf)
    await fm.send_message(message)
  


