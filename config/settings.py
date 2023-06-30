#
#               |    |   _)
#    __|   _ \  __|  __|  |  __ \    _` |   __|     __ \   |   |
#  \__ \   __/  |    |    |  |   |  (   | \__ \     |   |  |   |
#  ____/ \___| \__| \__| _| _|  _| \__, | ____/ _)  .__/  \__, |
#                                  |___/           _|     ____/
#

from pydantic import BaseSettings
from functools import lru_cache
from datetime import timedelta
import os


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    SECRET_KEY = '4e83e37965e4ae1723f5134d11db92ffb7757f8a9309632ab4fecae1cff3c09e'
    ALGORITHM = "HS256"
    TOKEN_LIFETIME = timedelta(hours=24)

    # SQLite
    DB_ABS_PATH = os.path.join(BASE_DIR, 'database/sqlite.db')
    DATABASE_URL = f'sqlite+aiosqlite:///{DB_ABS_PATH}'

    # PostgreSQL
    # DATABASE_HOST: str = 'localhost'
    # DATABASE_PORT: str = '5432'
    # DATABASE_NAME: str = 'chat'
    # DATABASE_USER: str = 'chat_user'
    # DATABASE_PASSWORD: str = 'chat_user'
    # DATABASE_URL = f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

    # Set True if database is SQLite otherwise False
    RENDER_AS_BATCH = True

    LOGIN_URL = '/auth/login'

    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


@lru_cache()
def get_settings():
    return Settings()
