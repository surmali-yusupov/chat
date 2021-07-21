from sqlalchemy import Integer, String, Boolean, Column, Table, ForeignKey, TypeDecorator
from database.database import metadata
import enum


class EnumInteger(TypeDecorator):
    impl = Integer

    def __init__(self, enum_type):
        super(EnumInteger, self).__init__()
        self.enum_type = enum_type

    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enum_type):
            return value.value
        raise ValueError('expected {0} value, got {1}'.format(self.enum_type.__name__, value.__class__.__name__))

    def process_result_value(self, value, dialect):
        return self.enum_type(value)

    # def values_callable(self):
    #     lambda x: [e.value for e in x]

    def copy(self, **kwargs):
        return EnumInteger(self.enum_type)


class ChatType(enum.Enum):
    PRIVATE = 1
    GROUP = 2


UserTable = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('username', String(32), unique=True, index=True, nullable=False),
    Column('password', String(32), nullable=False),
    Column('is_active', Boolean, server_default='1'),
    Column('is_superuser', Boolean, server_default='0'),
)

ContactTable = Table(
    'contacts', metadata,
    Column('user_id1', Integer, ForeignKey('users.id'), primary_key=True),
    Column('user_id2', Integer, ForeignKey('users.id'), primary_key=True),
)

ChatTable = Table(
    'chats', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('name', String(48), server_default=''),
    Column('creator', Integer, ForeignKey('users.id'), nullable=True),
    # Column('type', EnumInteger(ChatType), server_default=ChatType.PRIVATE),
)

ParticipantTable = Table(
    'participants', metadata,
    Column('chat_id', Integer, ForeignKey('chats.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
)

# class UserTable(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True, unique=True, index=True)
#     username = Column(String(50), unique=True, index=True, nullable=False)
#     password = Column(String(50), nullable=False)
#     is_active = Column(Boolean, default=True)
#     is_superuser = Column(Boolean, default=False)
