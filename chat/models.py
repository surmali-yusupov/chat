from sqlalchemy import Integer, String, Column, Table, ForeignKey, CheckConstraint
from database.database import metadata
import enum


class ChatType(enum.Enum):
    PRIVATE = 1
    GROUP = 2


ChatTable = Table(
    'chats', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String(48), server_default=''),
    Column('creator', Integer, ForeignKey('users.id'), nullable=True),
    Column('type', Integer, server_default=str(ChatType.PRIVATE.value)),
    # CheckConstraint("type = ANY(ARRAY[{0}])".format(','.join(str(i.value) for i in ChatType)), name='check_type')
)

ParticipantTable = Table(
    'participants', metadata,
    Column('chat_id', Integer, ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)
