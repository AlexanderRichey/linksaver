from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Optional


class UserForm(BaseModel):
    email: EmailStr
    password: str = Field(regex=r"^\w{6,}$")


class NoteForm(BaseModel):
    title: Optional[str] = None
    body: str
    csrf: str

    @validator("body")
    def body_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("body cannot be empty")
        return v


class LinkForm(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    url: HttpUrl
    favicon: Optional[HttpUrl] = None
    csrf: str
