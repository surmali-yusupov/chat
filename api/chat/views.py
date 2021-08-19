from core.utils import WSChatConnectionManager, WSUserConnectionManager
from chat.models import ChatTable, ParticipantTable, ChatType
from fastapi import WebSocket, APIRouter, Body, Depends
from auth.oauth import get_current_active_user
from chat.utils import get_chat_participants
from auth.decorators import login_required
from chat.constants import ChatAction
from chat.schemes import ChatCreate
from database.database import db
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
async def ws_chat(websocket: WebSocket, user: int, chat: int):
    try:
        await ws_chat_manager.connect(chat, user, websocket)
        while True:
            data = await websocket.receive_text()
            await ws_chat_manager.notify_subscribers(chat, data)
    except Exception:
        await ws_chat_manager.disconnect(chat, user)


@router.post('/chat/create')
@login_required
async def create_chat(data: ChatCreate, user: User = Depends(get_current_active_user)):
    chat_values = {'creator': user.id, 'type': data.type}
    if data.type == ChatType.GROUP.value:
        chat_values['name'] = data.name
    query1 = ChatTable.insert().values(chat_values)
    async with db.connect() as conn:
        res = await conn.execute(query1)
        chat_id = res.inserted_primary_key['id']
        participants = [{'chat_id': chat_id, 'user_id': user.id}]
        for p in data.participants:
            participants.append({'chat_id': chat_id, 'user_id': p})
        query2 = ParticipantTable.insert().values(participants)
        await conn.execute(query2)
        await conn.commit()
        create_data = json.dumps(
            {'id': chat_id, 'sender': user.id, 'receivers': data.participants,
             'participants': [p['user_id'] for p in participants],
             'name': data.name, 'type': data.type, 'action': ChatAction.CREATE.value}
        )
        await ws_user_manager.notify_subscribers(create_data)
        status_data = json.dumps(
            {'sender': user.id, 'receivers': [p['user_id'] for p in participants], 'action': ChatAction.CONNECT.value}
        )
        await ws_user_manager.notify_subscribers(status_data)
        return {'id': chat_id}


@router.post('/chat/remove')
@login_required
async def remove_chat(chat_id: int = Body(...), user: User = Depends(get_current_active_user)):
    fetch = ChatTable.select().where(ChatTable.c.id == chat_id)
    participants = await get_chat_participants(chat_id)
    receivers = [p.id for p in participants]
    async with db.connect() as conn:
        res = await conn.execute(fetch)
        chat = res.fetchone()
        if chat['type'] == ChatType.PRIVATE.value or (chat['type'] == ChatType.GROUP.value and chat['creator'] == user.id):
            query = ChatTable.delete().where(ChatTable.c.id == chat_id)
            remove_data = json.dumps(
                {'id': chat_id, 'receivers': receivers, 'action': ChatAction.REMOVE.value}
            )
            await ws_user_manager.notify_subscribers(remove_data)
        else:
            query = ParticipantTable.delete() \
                .where(ParticipantTable.c.chat_id == chat_id, ParticipantTable.c.user_id == user.id)
            leave_data = json.dumps(
                {'id': chat_id, 'receivers': receivers, 'action': ChatAction.LEAVE.value}
            )
            await ws_user_manager.notify_subscribers(leave_data)
        await conn.execute(query)
        await conn.commit()
