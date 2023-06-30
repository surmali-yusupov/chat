#
#       |         |             |
#    _` |   _` |   __|   _` |  __ \    _` |   __|   _ \     __ \   |   |
#   (   |  (   |   |    (   |  |   |  (   | \__ \   __/     |   |  |   |
#  \__,_| \__,_|  \__| \__,_| _.__/  \__,_| ____/ \___| _|  .__/  \__, |
#                                                          _|     ____/
#

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from config.settings import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL)

async_session = async_sessionmaker(engine)
