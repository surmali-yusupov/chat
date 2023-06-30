from .utils import authenticate_user, create_access_token, hash_password, create_user
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from .schemes import TokenData, SignupModel, LoginModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from templates.templates import templates
from config.settings import get_settings
from typing import Optional

settings = get_settings()
router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/token', response_model=TokenData, tags=['token'])
async def token(form_data=Depends(OAuth2PasswordRequestForm)):
    user = await authenticate_user(form_data.username, form_data.password)
    access_token = await create_access_token(data={'sub': user.username}, expires_delta=settings.TOKEN_LIFETIME)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/signup', response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse('registration/signup.html', {'request': request})


@router.post('/signup', tags=['signup'])
async def signup_page(request: Request, next: Optional[str] = Query('/')):
    form_data = await request.form()
    form = SignupModel(**form_data)
    if form.password1 != form.password2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect password confirmation')
    hashed_password = hash_password(form.password1)
    await create_user(form.username, hashed_password)
    access_token = await create_access_token(data={'sub': form.username}, expires_delta=settings.TOKEN_LIFETIME)
    token = jsonable_encoder(access_token)
    response = RedirectResponse(url=next, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie('Authorization', value=f'Bearer {token}', domain=request.base_url.hostname, httponly=True, max_age=3600 * 24, expires=3600 * 24)
    return response


@router.get('/login', response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse('registration/login.html', {'request': request})


@router.post('/login', tags=['login'])
async def login(request: Request, next: Optional[str] = Query('/')):
    form_data = await request.form()
    form = LoginModel(**form_data)
    user = await authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect email or password')
    access_token = await create_access_token(data={'sub': form.username}, expires_delta=settings.TOKEN_LIFETIME)
    token = jsonable_encoder(access_token)
    response = RedirectResponse(url=next, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie('Authorization', value=f'Bearer {token}', domain=request.base_url.hostname,
                        httponly=True, max_age=60 * 60 * 24, expires=60 * 60 * 24)
    return response


@router.get('/logout')
async def logout():
    response = RedirectResponse(url='/')
    response.delete_cookie('Authorization')
    return response

# @router.post('/login-basic', tags=['login'])
# async def login_basic(auth: BasicAuth = Depends(basic_auth), next: Optional[str] = Query('/')):
#     try:
#         decoded = base64.b64decode(auth).decode('ascii')
#         username, _, password = decoded.partition(':')
#         user = await authenticate_user(username, password)
#         if not user:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect email or password')
#         access_token = await create_access_token(data={'sub': username}, expires_delta=settings.TOKEN_LIFETIME)
#         token = jsonable_encoder(access_token)
#         response = RedirectResponse(url=next)
#         response.set_cookie('Authorization', value=f'Bearer {token}', domain='localhost', httponly=True, max_age=3600 * 24, expires=3600 * 24)
#         return response
#     except:
#         response = Response(headers={'WWW-Authenticate': 'Basic'}, status_code=status.HTTP_401_UNAUTHORIZED)
#         return response
