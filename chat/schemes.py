#
#               |
#    __|   __|  __ \    _ \  __ `__ \    _ \   __|     __ \   |   |
#  \__ \  (     | | |   __/  |   |   |   __/ \__ \     |   |  |   |
#  ____/ \___| _| |_| \___| _|  _|  _| \___| ____/ _)  .__/  \__, |
#                                                     _|     ____/
#

from typing import Optional, List
from chat.models import ChatType
from pydantic import BaseModel


class Participant(BaseModel):
    id: int
    username: str


class Chat(BaseModel):
    id: int
    type: int = ChatType.PRIVATE.value
    name: Optional[str] = ''
    creator: Optional[int] = None
    participants: List[Participant] = []


class ChatCreate(BaseModel):
    type: Optional[int] = ChatType.PRIVATE.value
    name: Optional[str] = ''
    participants: List[int]
