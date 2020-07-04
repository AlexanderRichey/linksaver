from secrets import token_urlsafe
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, HttpUrl, validator
from starlette.authentication import BaseUser
from bson.objectid import ObjectId

from .db import db


TYPE_NOTE = "note"
TYPE_LINK = "link"


class AnonUser(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        return False

    @property
    def display_name(self) -> str:
        return "unknown"

    @property
    def identity(self) -> str:
        return "unknown"


class User(BaseModel, BaseUser):
    email: EmailStr
    password_digest: str
    session_id: str = token_urlsafe(16)
    token: str = token_urlsafe(16)
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @classmethod
    def get_by_session_id(cls, session_id):
        user = db.users.find_one({"session_id": session_id})
        if not user:
            return None
        return cls.construct(**user)

    @classmethod
    def get_by_token(cls, token):
        user = db.users.find_one({"token": token})
        if not user:
            return None
        return cls.construct(**user)

    @classmethod
    def get_by_email(cls, email):
        user = db.users.find_one({"email": email})
        if not user:
            return None
        return cls.construct(**user)

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.email

    @property
    def identity(self) -> str:
        return self.email

    def put(self):
        self.updated_at = datetime.now()
        db.users.replace_one({"email": self.email}, dict(self), True)
        return self

    def delete(self):
        db.users.delete_one({"email": self.email})
        return self

    def roll_session(self):
        self.session_id = token_urlsafe(16)


class Item(BaseModel):
    id: Optional[str]
    email: EmailStr
    type: Literal[TYPE_LINK, TYPE_NOTE]
    url: Optional[HttpUrl] = None
    favicon: Optional[HttpUrl] = None
    title: Optional[str] = None
    body: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @validator("url")
    def url_not_none_for_links(cls, v, values):
        if values["type"] == TYPE_LINK and not v:
            raise ValueError("url required for links")
        return v

    @validator("body")
    def body_not_empty_for_notes(cls, v, values):
        if values["type"] == TYPE_NOTE and (not v or len(v) == 0):
            raise ValueError("body cannot be empty")
        return v

    @staticmethod
    def clean_item(item) -> dict:
        cleaned = {}
        for k, v in item.items():
            if k == "_id":
                cleaned["id"] = str(v)
            else:
                cleaned[k] = v
        return cleaned

    @classmethod
    def get_by_id(cls, id: str):
        item = db.items.find_one({"_id": ObjectId(id)})
        if not item:
            return None
        return cls.construct(**Item.clean_item(item))

    @staticmethod
    def get_by_user(user: User):
        items = []
        for item in db.items.find({"email": user.email}):
            items.append(Item.construct(**Item.clean_item(item)))
        return items

    def put(self):
        self.updated_at = datetime.now()
        resp = db.items.replace_one(
            {"_id": ObjectId(self.id)},
            {k: v for k, v in dict(self).items() if k != "id"},
            True,
        )
        self.id = str(resp.upserted_id) if resp.upserted_id else self.id
        return self

    def delete(self):
        db.items.delete_one({"_id": ObjectId(self.id)})
        return self
