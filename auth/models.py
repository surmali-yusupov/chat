from sqlalchemy import String, Boolean, Table, Column, Integer
from database.models import Base

_user_table = Table(
    'users', Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('username', String(32), unique=True, index=True, nullable=False),
    Column('password', String(128), nullable=False),
    Column('is_active', Boolean, server_default='1'),
    Column('is_superuser', Boolean, server_default='0'),
    Column('color', String(7), nullable=True, server_default='#1e8fa0'),
)


class UserTable(Base):
    __table__ = _user_table
