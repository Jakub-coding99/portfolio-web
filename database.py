from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select,JSON,Column

class Projects(SQLModel,table = True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    image_url: list[str] | None = Field(default=None, sa_column=Column(JSON))
    preview: str

class Admin(SQLModel, table = True):
    id: int | None = Field(default=None, primary_key=True)
    user_name: str
    password: str



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

