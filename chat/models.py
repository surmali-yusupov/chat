from sqlalchemy import String, ForeignKey, Integer, CheckConstraint, Table, Column
from database.models import Base
import enum


class ChatType(enum.Enum):
    PRIVATE = 1
    GROUP = 2


_chat_table = Table(
    'chats', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String(48), server_default=''),
    Column('creator', Integer, ForeignKey('users.id'), nullable=True),
    Column('type', Integer, server_default=str(ChatType.PRIVATE.value)),
    CheckConstraint('type IN ({0})'.format(','.join(str(i.value) for i in ChatType)), name='type_check_constraint')
)

_participant_table = Table(
    'participants', Base.metadata,
    Column('chat_id', Integer, ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
)


class ChatTable(Base):
    __table__ = _chat_table


class ParticipantTable(Base):
    __table__ = _participant_table
