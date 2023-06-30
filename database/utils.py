from database.database import engine, async_session
from sqlalchemy import text


async def dispose():
    await engine.dispose()


async def execute_raw(query: str, data, commit=True, scalar=False):
    async with async_session() as session:
        if scalar:
            result = await session.scalars(text(query), data)
        else:
            result = await session.execute(text(query), data)
        if commit:
            await session.commit()
    return result


async def execute_orm(query, data=None, commit=True, scalar=False):
    async with async_session() as session:
        if scalar:
            result = await session.scalars(query, data)
        else:
            result = await session.execute(query, data)
        if commit:
            await session.commit()
    return result


def row_to_dict(model, row):
    data = {}
    for column in model.__table__.columns:
        data[column.name] = str(getattr(row, column.name))
    return data
