from sqlalchemy.ext.asyncio import create_async_engine
from config.settings import get_settings
from sqlalchemy.engine import Engine
from sqlalchemy import event
import sqlalchemy

settings = get_settings()

db = create_async_engine(settings.DATABASE_URL)

metadata = sqlalchemy.MetaData()


def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute('PRAGMA foreign_keys=ON')
    cursor.close()


def db_configure():
    # Make SQLite cascade delete work
    if settings.DATABASE_URL.startswith('sqlite'):
        event.listens_for(Engine, 'connect')(set_sqlite_pragma)
