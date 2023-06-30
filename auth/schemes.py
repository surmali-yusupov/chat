from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=1, max_length=128)

    class Config:
        orm_mode = True


class LoginModel(UserBase):
    password: str = Field(..., min_length=5, max_length=128)

    class Config:
        orm_mode = True


class SignupModel(UserBase):
    password1: str = Field(..., min_length=5, max_length=128)
    password2: str = Field(..., min_length=5, max_length=128)


class User(UserBase):
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_authenticated: Optional[bool] = False
    color: Optional[str] = '#1e8fa0'
    password: Optional[str] = None

    class Config:
        orm_mode = True


class Contact(UserBase):
    id: int


class TokenData(BaseModel):
    access_token: str
    token_type: str
