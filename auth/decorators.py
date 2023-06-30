from fastapi.responses import RedirectResponse
from .exceptions import notAuthenticated
from config.settings import get_settings
from functools import wraps

settings = get_settings()


def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if 'user' in kwargs and kwargs['user'].is_authenticated:
            return await func(*args, **kwargs)
        raise notAuthenticated

    return wrapper


def login_redirect(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if 'user' in kwargs and kwargs['user'].is_authenticated:
            return await func(*args, **kwargs)
        return RedirectResponse(url=settings.LOGIN_URL)

    return wrapper
