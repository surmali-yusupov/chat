#
#          |   _)  |
#   |   |  __|  |  |   __|     __ \   |   |
#   |   |  |    |  | \__ \     |   |  |   |
#  \__,_| \__| _| _| ____/ _)  .__/  \__, |
#                             _|     ____/
#

from sqlalchemy.ext.asyncio import create_async_engine
from chat.utils import get_user_contacts
from config.settings import get_settings
from chat.constants import ChatAction
from typing import Dict, Optional
from fastapi import WebSocket
from redis import Redis
import threading
import asyncio
import json

settings = get_settings()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class RedisConnectionManager(metaclass=Singleton):
    def __init__(self):
        self.conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    def publish(self, channel: str, message: str):
        self.conn.publish(channel, message)


rc_manager = RedisConnectionManager()


class WSChatConnectionManager(metaclass=Singleton):
    def __init__(self):
        self.connections: Dict[str, Dict[int, WebSocket]] = {}

    async def connect(self, chat: str, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if chat in self.connections:
            self.connections[chat][user_id] = websocket
        else:
            self.connections[chat] = {user_id: websocket}

    async def disconnect(self, chat: str, user_id: int):
        self.connections[chat].pop(user_id)
        if not self.connections[chat]:
            self.connections.pop(chat)

    async def send_message(self, chat: str, message: str):
        connections = await self.match(chat)
        for ws in connections.values():
            await ws.send_text(message)

    async def notify_subscribers(self, chat: str, message: str):
        msg = json.dumps({'chat': chat, 'message': message})
        rc_manager.publish('chat', msg)

    async def match(self, chat: str) -> Dict[int, WebSocket]:
        try:
            return self.connections[chat]
        except:
            return {}


ws_chat_manager = WSChatConnectionManager()


class WSUserConnectionManager(metaclass=Singleton):
    def __init__(self):
        self.connections = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.connections[user_id] = websocket
        await self.notify_subscribers(json.dumps({'sender': user_id, 'action': ChatAction.CONNECT.value}))

    async def disconnect(self, user_id: int):
        self.connections.pop(user_id)
        await self.notify_subscribers(json.dumps({'sender': user_id, 'action': ChatAction.DISCONNECT.value}))

    async def match(self, user_id: int) -> Optional[WebSocket]:
        return self.connections[user_id] if user_id in self.connections else None

    async def notify_subscribers(self, data: str):
        rc_manager.publish('user', data)

    async def chat_action(self, data: dict):
        receivers = data['receivers']
        data = json.dumps(data)
        for r in receivers:
            ws = await self.match(r)
            if ws:
                await ws.send_text(data)

    async def notify_contacts(self, data: dict):
        db = create_async_engine(settings.DATABASE_URL)
        sender_id = data['sender']
        filter_contacts = data['receivers'] if 'receivers' in data else None
        contacts = await get_user_contacts(sender_id, filter_contacts, db)
        for c in contacts:
            ws = await self.match(c.id)
            if ws:
                await ws.send_text(json.dumps(data))
                response = json.dumps({'sender': c.id, 'receivers': [sender_id], 'action': ChatAction.CONNECT.value})
                await self.notify_subscribers(response)
        await db.dispose()


ws_user_manager = WSUserConnectionManager()


class Listener(threading.Thread):
    def __init__(self, conn, channels):
        threading.Thread.__init__(self)
        self.redis = conn
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        self.pubsub.subscribe(channels)

    def run(self):
        for msg in self.pubsub.listen():
            try:
                channel = msg['channel'].decode('utf-8')
                data = json.loads(msg['data'])
                if channel == 'chat':
                    asyncio.run(ws_chat_manager.send_message(data['chat'], data['message']))
                elif channel == 'user':
                    if data['action'] in [ChatAction.CREATE.value, ChatAction.REMOVE.value]:
                        asyncio.run(ws_user_manager.chat_action(data))
                    elif data['action'] in [ChatAction.CONNECT.value, ChatAction.DISCONNECT.value]:
                        asyncio.run(ws_user_manager.notify_contacts(data))
            except Exception as e:
                print(e)


listener = Listener(rc_manager.conn, ['chat', 'user'])

# async def listener():
#     pubsub.subscribe('chat')
#     while True:
#         msg = pubsub.get_message()
#         if msg:
#             try:
#                 data = json.loads(msg['data'])
#                 await ws_manager.send_message(data['chat'], data['message'])
#             except Exception as e:
#                 print(e)
#         await asyncio.sleep(0.01)
