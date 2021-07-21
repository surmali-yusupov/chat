from sqlalchemy.ext.asyncio import create_async_engine
from config.settings import get_settings
import sqlalchemy

settings = get_settings()

db = create_async_engine(settings.DATABASE_URL)

metadata = sqlalchemy.MetaData()
