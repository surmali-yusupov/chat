from pydantic import BaseModel, Field
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=128)


class LoginModel(UserBase):
    password: str = Field(..., min_length=5, max_length=128)


class SignupModel(UserBase):
    password1: str = Field(..., min_length=5, max_length=128)
    password2: str = Field(..., min_length=5, max_length=128)


class User(UserBase):
    id: Optional[int] = None
    color: Optional[str] = '#1e8fa0'
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_authenticated: Optional[bool] = False

    class Config:
        orm_mode = True


class Contact(UserBase):
    id: int


class TokenData(BaseModel):
    access_token: str
    token_type: str
