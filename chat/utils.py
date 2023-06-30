from chat.models import ChatTable, ParticipantTable, ChatType
from chat.schemes import Participant, Chat, ChatCreate
from sqlalchemy import select, insert, delete
from database.utils import execute_orm
from auth.schemes import Contact, User
from auth.models import UserTable
from pydantic import parse_obj_as
from typing import List, Tuple


async def get_chat(chat_id: int) -> Chat:
    query = select(ChatTable).where(ChatTable.id == chat_id)
    result = await execute_orm(query, commit=False, scalar=True)
    data = result.first()
    return Chat.from_orm(data)


async def create_chat(info: ChatCreate, user: User) -> int:
    data = info.dict()
    participants = data.pop('participants')
    data['creator'] = user.id
    if info.type == ChatType.GROUP.value:
        data['name'] = info.name
    query = insert(ChatTable).returning(ChatTable.id)
    result = await execute_orm(query, data, scalar=True)
    chat_id = result.first()
    query = insert(ParticipantTable)
    participants_data = [{'chat_id': chat_id, 'user_id': p} for p in participants]
    participants_data.append({'chat_id': chat_id, 'user_id': user.id})
    await execute_orm(query, participants_data)
    return chat_id


async def delete_chat(chat_id: int):
    query = delete(ChatTable).where(ChatTable.id == chat_id)
    await execute_orm(query)


async def delete_participant(chat_id: int, user_id: int):
    query = delete(ParticipantTable).where(ParticipantTable.chat_id == chat_id, ParticipantTable.user_id == user_id)
    await execute_orm(query)


async def get_user_chats(user_id: int, engine=None) -> List[Chat]:
    subq = select(ParticipantTable.chat_id).where(ParticipantTable.user_id == user_id).scalar_subquery()
    query = select(ChatTable.id, ChatTable.name, ChatTable.type, ChatTable.creator, UserTable.id, UserTable.username) \
        .join(ParticipantTable, ChatTable.id == ParticipantTable.chat_id) \
        .join(UserTable, UserTable.id == ParticipantTable.user_id) \
        .where(ChatTable.id.in_(subq), ParticipantTable.user_id != user_id) \
        .order_by(ChatTable.id)
    result = await execute_orm(query, commit=False)
    data = result.all()
    return await parse_chats(data)


async def parse_chats(data: List[Tuple]) -> List[Chat]:
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
    subq = select(ParticipantTable.chat_id).where(ParticipantTable.user_id == user_id).scalar_subquery()
    query = select(UserTable) \
        .join(ParticipantTable, UserTable.id == ParticipantTable.user_id) \
        .join(ChatTable, ChatTable.id == ParticipantTable.chat_id) \
        .distinct(ParticipantTable.user_id) \
        .where(ChatTable.id.in_(subq), ChatTable.type == ChatType.PRIVATE.value,
               ParticipantTable.user_id != user_id)
    if contacts:
        query = query.where(ParticipantTable.user_id.in_(contacts))
    result = await execute_orm(query, commit=False, scalar=True)
    data = result.all()
    return parse_obj_as(List[Contact], data)


async def get_chat_participants(id: int, engine=None) -> List[Contact]:
    query = select(UserTable) \
        .join(ParticipantTable, UserTable.id == ParticipantTable.user_id) \
        .where(ParticipantTable.chat_id == id)
    result = await execute_orm(query, commit=False, scalar=True)
    data = result.all()
    return parse_obj_as(List[Contact], data)
