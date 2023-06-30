#
#                             |                  |
#    __|   _ \   __ \    __|  __|   _` |  __ \   __|   __|     __ \   |   |
#   (     (   |  |   | \__ \  |    (   |  |   |  |   \__ \     |   |  |   |
#  \___| \___/  _|  _| ____/ \__| \__,_| _|  _| \__| ____/ _)  .__/  \__, |
#                                                             _|     ____/
#

from enum import Enum


class ChatAction(Enum):
    CONNECT = 1
    DISCONNECT = 2
    CREATE = 3
    REMOVE = 4
    LEAVE = 5
