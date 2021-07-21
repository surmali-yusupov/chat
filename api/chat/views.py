from core.utils import WSChatConnectionManager, WSUserConnectionManager
from fastapi import WebSocket, APIRouter, Body, Depends
from auth.oauth import get_current_active_user
from auth.decorators import login_required
from auth.models import ContactTable
from database.database import db
from sqlalchemy import or_, and_
from auth.schemes import User
import json

router = APIRouter()
ws_chat_manager = WSChatConnectionManager()
ws_user_manager = WSUserConnectionManager()


@router.websocket('/chat/{user}')
async def ws_user(websocket: WebSocket, user: int):
    try:
        await ws_user_manager.connect(user, websocket)
        while True:
            data = await websocket.receive_text()
            await ws_user_manager.notify_subscribers(data)
    except Exception:
        await ws_user_manager.disconnect(user)


@router.websocket('/chat/{user}/{chat}')
async def ws_chat(websocket: WebSocket, user: int, chat: str):
    try:
        await ws_chat_manager.connect(chat, user, websocket)
        while True:
            data = await websocket.receive_text()
            await ws_chat_manager.notify_subscribers(chat, data)
    except Exception:
        await ws_chat_manager.disconnect(chat, user)


@router.post('/chat/create')
@login_required
async def add_contact(id: int = Body(...), user: User = Depends(get_current_active_user)):
    query = ContactTable.insert().values([
        {'user_id1': id, 'user_id2': user.id},
        {'user_id1': user.id, 'user_id2': id},
    ])
    await ws_user_manager.notify_subscribers(json.dumps({'sender': user.id, 'action': 'connect'}))
    async with db.connect() as conn:
        await conn.execute(query)
        await conn.commit()


@router.post('/chat/remove')
@login_required
async def remove_contact(id: int = Body(...), user: User = Depends(get_current_active_user)):
    query = ContactTable.delete().where(
        or_(and_(ContactTable.c.user_id1 == user.id, ContactTable.c.user_id2 == id),
            and_(ContactTable.c.user_id2 == user.id, ContactTable.c.user_id1 == id))
    )
    async with db.connect() as conn:
        await conn.execute(query)
        await conn.commit()
