from chat.models import ChatTable, ParticipantTable, ChatType
from chat.schemes import Participant, Chat
from auth.models import UserTable
from pydantic import parse_obj_as
from auth.schemes import Contact
from database.database import db
from typing import List, Tuple
from sqlalchemy import select


async def get_user_chats(user_id: int, engine=None) -> List[Chat]:
    db_engine = engine if engine else db
    subq = select(ParticipantTable.c.chat_id).where(ParticipantTable.c.user_id == user_id)
    query = select([ChatTable.c.id, ChatTable.c.name, ChatTable.c.type, ChatTable.c.creator, UserTable.c.id, UserTable.c.username]) \
        .select_from(
        ParticipantTable
            .join(ChatTable, ChatTable.c.id == ParticipantTable.c.chat_id) \
            .join(UserTable, UserTable.c.id == ParticipantTable.c.user_id)) \
        .where(ChatTable.c.id.in_(subq.scalar_subquery()), ParticipantTable.c.user_id != user_id)
    async with db_engine.connect() as conn:
        res = await conn.execute(query)
        data = res.fetchall()
        return await parse_chats(data)


async def parse_chats(data: List[Tuple]) -> List[Chat]:
    data = sorted(data, key=lambda x: x[0])
    chat_id = c = None
    res = []
    for d in data:
        if d[0] != chat_id:
            name = d[1] if d[1] else d[5]
            c = Chat(id=d[0], name=name, type=d[2], creator=d[3])
            res.append(c)
            chat_id = d[0]
        c.participants.append(Participant(id=d[4], username=d[5]))
    return res


async def get_user_contacts(user_id: int, contacts=None, engine=None) -> List[Contact]:
    db_engine = engine if engine else db
    subq = select(ParticipantTable.c.chat_id) \
        .where(ParticipantTable.c.user_id == user_id)
    query = select([UserTable.c.id, UserTable.c.username]) \
        .select_from(
        ParticipantTable
            .join(ChatTable, ChatTable.c.id == ParticipantTable.c.chat_id) \
            .join(UserTable, UserTable.c.id == ParticipantTable.c.user_id)) \
        .distinct(ParticipantTable.c.user_id) \
        .where(ChatTable.c.id.in_(subq.scalar_subquery()),
               ChatTable.c.type == ChatType.PRIVATE.value,
               ParticipantTable.c.user_id != user_id)
    if contacts:
        query = query.where(ParticipantTable.c.user_id.in_(contacts))
    async with db_engine.connect() as conn:
        res = await conn.execute(query)
        data = res.fetchall()
        return parse_obj_as(List[Contact], data)


async def get_chat_participants(id: int, engine=None) -> List[Contact]:
    db_engine = engine if engine else db
    query = ParticipantTable \
        .select().with_only_columns([UserTable.c.id, UserTable.c.username]) \
        .join(UserTable, UserTable.c.id == ParticipantTable.c.user_id) \
        .where(ParticipantTable.c.chat_id == id)
    async with db_engine.connect() as conn:
        res = await conn.execute(query)
    data = res.fetchall()
    return parse_obj_as(List[Contact], data)

# select c.id, c.name, u.id, u.username
# from participants p
#          join chats c on c.id = p.chat_id
#          join users u on u.id = p.user_id
# where c.id in (select p.chat_id from participants p where p.user_id = 4);
