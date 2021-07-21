# from sqlalchemy import Integer, String, Column, Table
# from database.database import metadata
# from database.database import Base

# ChatTable = Table(
#     'chats', metadata,
#     Column('id', Integer, primary_key=True, unique=True, index=True),
#     Column('title', String(128), nullable=False),
# )


# class ChatTable(Base):
#     __tablename__ = 'chats'
#     id = Column(Integer, primary_key=True, unique=True, index=True)
#     title = Column(String(50), nullable=False)
