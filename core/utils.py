#
#          |   _)  |
#   |   |  __|  |  |   __|     __ \   |   |
#   |   |  |    |  | \__ \     |   |  |   |
#  \__,_| \__| _| _| ____/ _)  .__/  \__, |
#                             _|     ____/
#

from chat.utils import get_user_contacts, get_chat_participants
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
        self.connections: Dict[int, Dict[int, Optional[WebSocket]]] = {}
        self.redis = RedisConnectionManager()

    async def connect(self, chat: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if chat in self.connections:
            self.connections[chat][user_id] = websocket
        else:
            participants = await get_chat_participants(chat)
            self.connections[chat] = {}
            for p in participants:
                self.connections[chat][p.id] = None
            self.connections[chat][user_id] = websocket
        while True:
            msg = self.redis.conn.lpop(user_id)
            if not msg:
                break
            await websocket.send_text(msg.decode('utf-8'))

    async def disconnect(self, chat: int, user_id: int):
        self.connections[chat][user_id] = None
        if not self.connections[chat]:
            self.connections.pop(chat)
        else:
            for c in self.connections[chat].values():
                if c is not None:
                    break
            else:
                self.connections.pop(chat)

    async def send_message(self, chat: int, message: str):
        connections = await self.match(chat)
        for c, ws in connections.items():
            if ws is not None:
                msg = self.redis.conn.lpop(c).decode('utf-8')
                await ws.send_text(msg)

    async def notify_subscribers(self, chat: int, message: str):
        msg = json.dumps({'chat': chat, 'message': message})
        for c in self.connections[chat].keys():
            self.redis.conn.rpush(c, message)
            # expire in one day
            self.redis.conn.expire(c, 86400)
        self.redis.publish('chat', msg)

    async def match(self, chat: int) -> Dict[int, WebSocket]:
        return self.connections[chat] if chat in self.connections else {}


ws_chat_manager = WSChatConnectionManager()


class WSUserConnectionManager(metaclass=Singleton):
    def __init__(self):
        self.connections = {}
        self.redis = RedisConnectionManager()

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
        self.redis.publish('user', data)

    async def chat_action(self, data: dict):
        receivers = data['receivers']
        data = json.dumps(data)
        for r in receivers:
            ws = await self.match(r)
            if ws:
                await ws.send_text(data)

    async def notify_contacts(self, data: dict):
        sender_id = data['sender']
        respond = data.get('respond', True)
        filter_contacts = data['receivers'] if 'receivers' in data else None
        contacts = await get_user_contacts(sender_id, filter_contacts)
        for c in contacts:
            ws = await self.match(c.id)
            if ws:
                await ws.send_text(json.dumps(data))
                if respond:
                    response = json.dumps({'sender': c.id, 'receivers': [sender_id], 'action': ChatAction.CONNECT.value, 'respond': False})
                    await self.notify_subscribers(response)


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
