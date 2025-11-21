from fastapi import FastAPI,Request,Depends ,File, Form, UploadFile, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from passlib.context import CryptContext
from database import Projects, Admin,Blog,create_db_and_tables,engine,Session,select
import os
from typing import List
from fastapi.responses import RedirectResponse
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from dotenv import load_dotenv,find_dotenv
import markdown
import re
from itertools import zip_longest
from auth import router as auth_router
from core.core import templates



dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

ADMIN_URL = "/user/admin"
ADD_PROJECT_URL = "/add/{model_type}"
ADMIN_PAGE_URL = "/admin-page"
ADMIN_EDIT_PROJECT = "/edit/{model_type}/{id}"

MODEL = {
    "project": {
        "model" : Projects,
        "template_edit" : "admin/edit_content.html",
        "template_add" : "admin/add_project.html",
        "redirect" : ADMIN_URL,
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

security = HTTPBasic()

create_db_and_tables()

@app.get(ADMIN_URL,response_class = HTMLResponse)
def get_admin(credentials : Annotated[HTTPBasicCredentials,Depends(security)]):
        with Session(engine) as session:
            hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")
            admin = session.scalars(select(Admin)).first()
            check_pass = hasher.verify(credentials.password,admin.password)

            if admin.user_name == credentials.username and check_pass:
                return RedirectResponse(url=ADMIN_PAGE_URL)
            else:
        
                raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
                headers={"WWW-Authenticate": "Basic"},
            )


@app.get("/add-new",response_class = HTMLResponse)
def add_content(request : Request,admin=Depends(get_admin),model_type= str):
    
    
    
 
    return templates.TemplateResponse("admin/add_content.html",{"request":request,"api_url" : ADD_PROJECT_URL})



@app.post("/add/{model_type}",response_class = HTMLResponse,)

async def add_project(request : Request,title:str = Form(...),description:str = Form(...),files: List[UploadFile] = File(None),
                      preview:str = Form(...),admin=Depends(get_admin),model_type= str):
    config= MODEL.get(model_type)
    model = config["model"]
    img_path = []
    
    empty_data = all(len(x) == 0  for x in (title,description,preview))
    
    if empty_data == True and files == None:
        return JSONResponse({"redirect": ADMIN_PAGE_URL})
    if files == None:
        fallback_img = "static/img/no-img.jpg"
        img_path.append(fallback_img)
        
    
    else:
        await upload_img(files,None,img_path)

       
    
    html_text = markdown.markdown(description)
    markdown_text = description
    
    new_model = model(title=title, description=html_text,image_url=img_path,preview=preview,markdown=markdown_text)
    with Session(engine) as session:
        session.add(new_model)
        session.commit()
    
    return JSONResponse({"redirect": ADMIN_PAGE_URL})

   

@app.get(ADMIN_PAGE_URL, response_class=HTMLResponse)
def get_admin_pannel(request : Request,admin=Depends(get_admin)):
    projects = all_project()
    posts = blog_posts()
    return templates.TemplateResponse("admin/admin_main.html", {"request":request,"projects":projects,"posts":posts})


@app.get("/delete/{model_type}/{id}",response_class=HTMLResponse)
def delete_project(request:Request,id : int, model_type = str):
    config = MODEL.get(model_type)
   

    model = config["model"]
    
    with Session(engine) as session:
        app_path = os.path.dirname(os.path.abspath(__file__))
        choosen_model = session.get(model,id)
        if choosen_model:
            for img in choosen_model.image_url:
                if img == "static/img/no-img.jpg":
                    continue
                else:
                    try:
                        
                        to_del = f"{app_path}/{img}"
                        print(to_del)
                        os.remove(to_del)
                    except (FileNotFoundError, PermissionError):
                        
                        pass

            session.delete(choosen_model)
            session.commit()

    return RedirectResponse(url=ADMIN_PAGE_URL,status_code=303)

@app.get("/edit/{model_type}/{id}",response_class = HTMLResponse)
def get_edit_content(request:Request,id:int,model_type = str):
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


@app.post("/edit/{model_type}/{id}",response_class = HTMLResponse)
async def post_edit_content(request:Request,id:int,title: str = Form(...),description:str = Form(...),preview:str=Form(...),files: List[UploadFile] = File(None),model_type = str):
    config = MODEL.get(model_type)
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
        
        if choosen_model.preview != preview:
            choosen_model.preview = preview
        
        try:
            await upload_img(files,choosen_model,None)
            
            
        except TypeError:
            pass

        session.commit()
        return JSONResponse({"redirect": ADMIN_PAGE_URL})


async def upload_img(files,choosen_model,img_path):
    
    for file in files:
        print(file)
        DIR = "static/img/"
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
            project_format = {"id" : p.id,"title":p.title.upper(),"description":p.description,"img_url":p.image_url,
                              "preview":p.preview,"markdown":p.markdown,"endpoint":p.endpoint}
            projects.append(project_format)
    return projects


def blog_posts():
    posts = []
    with Session(engine) as session:
        blog = select(Blog)
        all_posts = session.scalars(blog).all()
        for p in all_posts:
            post_format = {"id" : p.id,"title":p.title.upper(),"description":p.description,"img_url":p.image_url,
                           "preview":p.preview,"markdown":p.markdown,"endpoint": p.endpoint}
            posts.append(post_format)
    
    return posts

def delete_img():

    all_projects = all_project()
    all_posts = blog_posts()
   
    
    if len(all_projects) == 0 and len(all_posts) ==0:
        return
    

    all_content = {
        "project": []

        ,
        "blog": []
        
    }

    for blog in all_posts:
        x = {"id" : blog["id"], "markdown":blog["markdown"],"img" : blog["img_url"],"new_imgs": []}
        all_content["blog"].append(x)

    for project in all_projects:
        y = {"id" : project["id"], "markdown":project["markdown"],"img" : project["img_url"],"new_imgs": []}
        all_content["project"].append(y)
        
    

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(BASE_DIR,"static/img")
    IMAGES = os.listdir(app_path)
    MY_IMG = ['favicon.ico', 'me.jpg', 'no-img.jpg']
    for my_img in MY_IMG:
        IMAGES.remove(my_img)
    
    images_in_md = []
    for (blog,project) in zip_longest(all_content['blog'],all_content['project'],fillvalue=None):
   
        blog_text = blog["markdown"] if blog else ""
        project_text = project["markdown"] if project else ""





        regex_blog = re.findall(r"static/img/[^\s)\"']+",blog_text)
        regex_project = re.findall(r"static/img/[^\s)\"']+",project_text)


        
        if regex_blog or regex_project:
            b_img = []
            p_img = []
            for(b,p) in zip_longest(regex_blog,regex_project,fillvalue=None):
                
                if b:
                    b_img.append(b)
                    images_in_md.append(b)
               
                if p:
                    p_img.append(p)
                    images_in_md.append(p)
                
            
            if blog:
                blog["new_imgs"] = b_img
            if project:
                project["new_imgs"] = p_img

    no_none_img = [x for x in images_in_md if x != None]

    images_in_md_splitted = [os.path.basename(i) for i in no_none_img]
    print(images_in_md_splitted)

    # print(f"toto jsou obrazky nachazejici v markdownu: {images_in_md_splitted}")

    
    img_to_del = [x for x in IMAGES if x not in images_in_md_splitted]
    # print(f"toto jsou obrazky, ktere budou smazany: {img_to_del}")

    if len(img_to_del) == 0:
        return
    
    
    with Session(engine) as session:
        for blog in all_content["blog"]:
            if blog["new_imgs"] is not None:
                db_blog = session.scalar(select(Blog).filter_by(id = blog["id"]))
                db_blog.image_url = blog["new_imgs"]
        
        for project in all_content["project"]:
            if project["new_imgs"] is not None:
                db_project = session.scalar(select(Projects).filter_by(id = project["id"]))
                db_project.image_url = project["new_imgs"]
     
        session.commit()
            
    for delete in img_to_del:
        try:
            os.remove(os.path.join(app_path, delete))
        
        except (FileNotFoundError):
            pass
            


app.mount("/static",StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def home(request : Request):
    projects = all_project()
    delete_img()
    
    
    
    return templates.TemplateResponse("index.html",{"request":request, "projects" : projects})


@app.get("/projects/{id}",response_class=HTMLResponse)
def get_project(request : Request ,id : int):
    
    all_projects = all_project()
    
    for p in all_projects:
        
        if p["id"] == id:
            project = p
            break

    if project is None:
        return HTMLResponse("<p>chyba</p>",status_code=404)
    return templates.TemplateResponse("projects.html", {"request":request, "project" : project})
    

@app.post("/submit_contact",response_class=HTMLResponse)
async def contact(request:Request):
    form_data = await request.form()
    data = dict(form_data)
    await send_email(data)
    return RedirectResponse(url="/#contact",status_code=303)



@app.get("/blog",response_class=HTMLResponse)
def blog(request:Request):
    posts = blog_posts()
    print(posts)
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
    return templates.TemplateResponse("post_template.html", {"request":request, "post" : post})
    


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
  


