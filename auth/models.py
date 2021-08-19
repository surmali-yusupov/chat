from sqlalchemy import Integer, String, Boolean, Column, Table
from database.database import metadata

UserTable = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('username', String(32), unique=True, index=True, nullable=False),
    Column('password', String(128), nullable=False),
    Column('is_active', Boolean, server_default='1'),
    Column('is_superuser', Boolean, server_default='0'),
    Column('color', String(7), nullable=True, server_default='#1e8fa0'),
)

# ContactTable = Table(
#     'contacts', metadata,
#     Column('user_id1', Integer, ForeignKey('users.id'), primary_key=True),
#     Column('user_id2', Integer, ForeignKey('users.id'), primary_key=True),
# )
