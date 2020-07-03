from pydantic import BaseModel, EmailStr, Field


class UserForm(BaseModel):
    email: EmailStr
    password: str = Field(regex=r"^\w{6,}$")
