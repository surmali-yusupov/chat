from auth.utils import hash_password, create_access_token, create_user, search_users
from auth.schemes import User, TokenData, LoginModel
from auth.oauth import get_current_active_user
from fastapi import APIRouter, Depends, Query
from auth.decorators import login_required
from config.settings import get_settings
from typing import List

settings = get_settings()
router = APIRouter(prefix='/user', tags=['user'])


@router.get('/search', response_model=List[User])
@login_required
async def users_list(q: str = Query(..., max_length=255), user: User = Depends(get_current_active_user)):
    users = await search_users(q, limit=10)
    users = list(filter(lambda x: x.id != user.id, users))
    return users


@router.get('/me', response_model=User)
@login_required
async def users_me(user: User = Depends(get_current_active_user)):
    return user


@router.post('/register', response_model=TokenData)
async def user_create(user: LoginModel):
    hashed_password = hash_password(user.password)
    await create_user(user.username, hashed_password)
    access_token = await create_access_token(data={'sub': user.username}, expires_delta=settings.TOKEN_LIFETIME)
    return {'access_token': access_token, 'token_type': 'bearer'}
