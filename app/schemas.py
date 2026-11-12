
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


class UserRegister(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class BlogCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    content: str = Field(min_length=10)
    category: str
    tags: list[str] = []
    image_url: Optional[str] = None
    status: Literal["draft", "published"] = "draft"


class BlogUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=150)
    content: Optional[str] = Field(default=None, min_length=10)
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    image_url: Optional[str] = None
    status: Optional[Literal["draft", "published"]] = None


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: Optional[str] = None
