from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import Integer


class Base(AsyncAttrs, DeclarativeBase):
    pass


class BaseId(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
