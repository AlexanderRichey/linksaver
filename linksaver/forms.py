from pydantic import BaseModel, EmailStr, Field, HttpUrl, validator
from typing import Optional
from datetime import datetime


class UserForm(BaseModel):
    email: EmailStr
    password: str

    @validator("password")
    def password_long_enough(cls, v):
        if len(v) < 5:
            raise ValueError("password must be at least 6 characters long")
        return v


class NoteForm(BaseModel):
    body: str
    title: str = ""
    csrf: str

    @validator("body")
    def body_not_empty(cls, v):
        if len(v) == 0:
            raise ValueError("body cannot be empty")
        return v

    @validator("title", always=True)
    def derive_title(cls, v, values):
        if "body" in values:
            split = values["body"].split("\n")
            if len(split) > 0 and len(split[0]) > 1:
                return split[0].strip(" #")[:64]
        timestamp = datetime.now().strftime("%-I:%M %p")
        return f"Note @ {timestamp}"


class LinkForm(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    url: HttpUrl
    favicon: Optional[HttpUrl] = None
    csrf: str


class ApiLinkForm(BaseModel):
    title: Optional[str] = None
    url: HttpUrl
    favicon: Optional[HttpUrl] = None
