from .exceptions import UserNotFound, IncorrectPassword, notAuthenticated
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from passlib.context import CryptContext
from datetime import timedelta, datetime
from config.settings import get_settings
from .schemes import User, LoginModel
from fastapi.security import OAuth2
from typing import Optional, Dict
from database.database import db
from .models import UserTable
from fastapi import Request
from jose import jwt

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
settings = get_settings()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


async def get_user(username: str) -> User:
    query = UserTable.select().where(UserTable.c.username == username)
    async with db.connect() as conn:
        response = await conn.execute(query)
        data = response.fetchone()
        if data:
            return User(**data)
    raise UserNotFound


async def authenticate_user(username: str, password: str) -> LoginModel:
    query = UserTable.select().where(UserTable.c.username == username)
    async with db.connect() as conn:
        response = await conn.execute(query)
        data = response.fetchone()
        if data:
            user = LoginModel(**data)
            if not verify_password(password, user.password):
                raise IncorrectPassword
            return user
    raise UserNotFound


async def create_user(username: str, password: str, is_active=True, is_superuser=False):
    color = await generate_user_color(username)
    query = UserTable.insert() \
        .values(username=username,
                password=password,
                is_active=is_active,
                is_superuser=is_superuser,
                color=color)
    async with db.connect() as conn:
        await conn.execute(query)
        await conn.commit()


async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


class OAuth2PasswordBearerCookie(OAuth2):
    def __init__(self, tokenUrl: str, scheme_name: Optional[str] = None, scopes: Optional[Dict[str, str]] = None,
                 auto_error: bool = True):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={'tokenUrl': tokenUrl, 'scopes': scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get('Authorization')
        cookie_authorization: str = request.cookies.get('Authorization')
        header_scheme, header_param = get_authorization_scheme_param(header_authorization)
        cookie_scheme, cookie_param = get_authorization_scheme_param(cookie_authorization)
        if header_scheme.lower() == 'bearer':
            param = header_param
        elif cookie_scheme.lower() == 'bearer':
            param = cookie_param
        else:
            if self.auto_error:
                raise notAuthenticated
            else:
                return None
        return param


async def generate_user_color(username: str):
    sum = 0
    bg_color = '#'
    for letter in username:
        sum += ord(letter)
    for i in range(3):
        x = sum % 256
        sum -= x * ((i + 1) * 42)
        bg_color += format(max(min(x, 160), 30), '02x')
    return bg_color
