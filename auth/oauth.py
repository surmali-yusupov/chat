from .utils import get_user, OAuth2PasswordBearerCookie
from config.settings import get_settings
from .exceptions import inactiveUser
from fastapi import Depends
from .schemes import User
from jose import jwt

oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl='/auth/token', auto_error=False)
settings = get_settings()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            return User(username='Anonymous')
        user = await get_user(username=username)
        if user is None:
            return User(username='Anonymous')
    except Exception:
        return User(username='Anonymous')
    user.is_authenticated = True
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.is_active:
        return current_user
    raise inactiveUser

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         username: str = payload.get('sub')
#         if username is None:
#             raise CredentialsError
#     except JWTError:
#         raise CredentialsError
#     user = await get_user(username=username)
#     if user is None:
#         raise CredentialsError
#     return user
#
#
# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.is_active:
#         return current_user
#     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
