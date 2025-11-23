from typing import List
import os
from sqlmodel import Field, Session, SQLModel, create_engine, select,JSON,Column
from sqlalchemy.ext.mutable import MutableList

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



sqlite_file_name = os.getenv("sqlite_file_name")
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

