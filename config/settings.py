from pydantic import BaseSettings
from functools import lru_cache
from datetime import timedelta
import os


class Settings(BaseSettings):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SECRET_KEY = '4e83e37965e4ae1723f5134d11db92ffb7757f8a9309632ab4fecae1cff3c09e'
    ALGORITHM = "HS256"
    TOKEN_LIFETIME = timedelta(hours=24)

    # DB_ABS_PATH = os.path.join(BASE_DIR, 'database/sqlite.db')
    # DATABASE_URL = f'sqlite+aiosqlite:///{DB_ABS_PATH}'
    DATABASE_URL = "postgresql+asyncpg://chatapp:chatapp@localhost:5432/chatapp"

    # Set True if database is SQLite otherwise False
    # RENDER_AS_BATCH = True

    LOGIN_URL = '/auth/login'

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


@lru_cache()
def get_settings():
    return Settings()
