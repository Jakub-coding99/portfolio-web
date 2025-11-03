from fastapi import FastAPI,Request,Depends ,File, Form, UploadFile, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated
from passlib.context import CryptContext
from database import Projects, Admin,create_db_and_tables,engine,Session,select
import os
from typing import List
from fastapi.responses import RedirectResponse
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from dotenv import load_dotenv,find_dotenv
import markdown


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

ADMIN_URL = "/user/admin"
ADD_PROJECT_URL = "/admin-add_project"
ADMIN_PAGE_URL = "/admin-page"
ADMIN_EDIT_PROJECT = "/edit/project/{id}"


app = FastAPI()

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


@app.get(ADD_PROJECT_URL,response_class = HTMLResponse)
def get_add_project(request : Request,admin=Depends(get_admin)):
    return templates.TemplateResponse("admin/admin_add_project.html",{"request":request,"api_url" : ADD_PROJECT_URL})



@app.post(ADD_PROJECT_URL,response_class = HTMLResponse,)

async def add_project(request : Request,title:str = Form(...),description:str = Form(...),files: List[UploadFile] = File(None),
                      preview:str = Form(...),admin=Depends(get_admin)):
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
    
    new_project = Projects(title=title, description=html_text,image_url=img_path,preview=preview,markdown=markdown_text)
    with Session(engine) as session:
        session.add(new_project)
        session.commit()
    
    return JSONResponse({"redirect": ADMIN_PAGE_URL})

   

@app.get(ADMIN_PAGE_URL, response_class=HTMLResponse)
def get_admin_pannel(request : Request,admin=Depends(get_admin)):
    projects = all_project()
    return templates.TemplateResponse("admin/admin_main.html", {"request":request,"projects":projects})


@app.get("/project/{id}",response_class=HTMLResponse)
def delete_project(request:Request,id : int):
    with Session(engine) as session:
        app_path = os.path.dirname(os.path.abspath(__file__))
        choosen_project = session.get(Projects,id)
        if choosen_project:
            for img in choosen_project.image_url:
                if img == "static/img/no-img.jpg":
                    continue
                else:
                    try:
                        
                        to_del = f"{app_path}/{img}"
                        print(to_del)
                        os.remove(to_del)
                    except (FileNotFoundError, PermissionError):
                        
                        pass

            session.delete(choosen_project)
            session.commit()

    return RedirectResponse(url=ADMIN_PAGE_URL,status_code=303)

@app.get(ADMIN_EDIT_PROJECT,response_class = HTMLResponse)
def get_edit_project(request:Request,id:int):
    delete_img()
    with Session(engine) as session:
        current_img = []
        project = session.get(Projects,id)
        images = project.image_url
        for i in images:
            x = i.split("/")
            img = {"name":x[2],"path":i}
            current_img.append(img)
        project.image_url = current_img
        
        
    return templates.TemplateResponse("admin/edit_project.html",{"request":request,"project":project})


@app.post(ADMIN_EDIT_PROJECT,response_class = HTMLResponse)
async def post_edit_project(request:Request,id:int,title: str = Form(...),description:str = Form(...),preview:str=Form(...),files: List[UploadFile] = File(None)):
    markdown_text = description
    with Session(engine) as session:
        project = session.get(Projects,id)
        if not project:
            return {"eror":"not found"}
        
        if project.title != title:
            project.title = title
        
        if project.markdown != markdown_text:
            new_description = markdown.markdown(markdown_text)
            project.description = new_description
            project.markdown = markdown_text
        
        if project.preview != preview:
            project.preview = preview
        
        try:
            await upload_img(files,project,None)
            
            
        except TypeError:
            pass

        session.commit()
        return JSONResponse({"redirect": ADMIN_PAGE_URL})


async def upload_img(files,project,img_path):
    
    for file in files:
       
        DIR = "static/img/"
        os.makedirs(DIR,exist_ok=True)
        location_file = os.path.join(DIR,file.filename)
       
        if project:
            project.image_url.append(location_file)
        
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
            project_format = {"id" : p.id,"title":p.title.upper(),"description":p.description,"img_url":p.image_url,"preview":p.preview,"markdown":p.markdown}
            projects.append(project_format)
   
    
    return projects

def delete_img():
    import re

    all_markdowns = []
    all_projects = all_project()
    projects_update = []
    
    if len(all_projects) == 0:
        return

    for project in all_projects:
        pr = {"project_id" : project["id"], "project_markdown":project["markdown"],"project_img" : project["img_url"],"new_imgs": []}
        projects_update.append(pr)
        all_markdowns.append(project["markdown"])
   

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(BASE_DIR,"static/img")
    IMAGES = os.listdir(app_path)
    MY_IMG = ['favicon.ico', 'me.jpg', 'no-img.jpg']
    for my_img in MY_IMG:
        IMAGES.remove(my_img)
    
    images_in_md = []

    for md in projects_update:
        text = md["project_markdown"]
        regex = re.findall("(static/img/.+\\w)",text)
        if len(regex) != 0:
            test_img = []
            for r in regex:
                test_img.append(r)
                images_in_md.append(r)
            # print(f"v projektu id: {md["project_id"]} se nachází tyto obrázky: {test_img}")
            md["new_imgs"] = test_img
    
    images_in_md_splitted = [i.split("/")[2] for i in images_in_md]
    # print(f"toto jsou obrazky nachazejici v markdownu: {images_in_md_splitted}")
    img_to_del = [x for x in IMAGES if x not in images_in_md_splitted]
    # print(f"toto jsou obrazky, ktere budou smazany: {img_to_del}")

    if len(img_to_del) == 0:
        return
    
    
    with Session(engine) as session:
        for p in projects_update:
    
            db_projects = session.scalar(select(Projects).filter_by(id = p["project_id"]))
            
            db_projects.image_url = p["new_imgs"]
           
           
     
            print(f"test: {db_projects.image_url}")
            session.commit()
            
    for delete in img_to_del:
        os.remove(f"{app_path}/{delete}")


app.mount("/static",StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
  


