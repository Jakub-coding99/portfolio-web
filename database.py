from typing import List
import os
from sqlmodel import Field, Session, SQLModel, create_engine,JSON,Column,select
from sqlalchemy.ext.mutable import MutableList
from dotenv import load_dotenv,find_dotenv
from sqlmodel import create_engine

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

class Projects(SQLModel,table = True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    preview: str
    markdown: str
    image_url: List[str] = Field(sa_column=Column(MutableList.as_mutable(JSON),default=list, nullable=False))
    endpoint: str = Field(default="project", nullable=False)

class Blog(SQLModel,table = True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    preview: str
    markdown: str
    image_url: List[str] = Field(sa_column=Column(MutableList.as_mutable(JSON),default=list, nullable=False))
    endpoint: str = Field(default="blog", nullable=False)

class Admin(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True)
    user_name: str
    password: str




DATABASE_URL = os.getenv("DB_URL")



connect_args = {"check_same_thread": False}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# engine = create_engine(DATABASE_URL,
#                         echo=True,
#                         max_overflow=10,
#                         pool_pre_ping=True,
#                         pool_size=5,
#                         pool_recycle=1800)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)