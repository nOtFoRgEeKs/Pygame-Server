from __future__ import annotations

import pickle

from protocol import Command, Status


class GameData:

    def __init__(self, **kwargs):
        self.add_data(**kwargs)

    def add_data(self, **kwargs):
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])

    def __repr__(self):
        return str(self.__dict__)


class BaseMessage:
    @classmethod
    def encode(cls, message: BaseMessage) -> bytes:
        if not isinstance(message, cls):
            raise TypeError('Object of ' + cls.__name__ + ' expected')
        else:
            return pickle.dumps(message)

    @classmethod
    def decode(cls, stream: bytes) -> BaseMessage:
        object_ = pickle.loads(stream)
        if isinstance(object_, cls):
            return object_
        else:
            raise TypeError('Object of ' + cls.__name__ + ' expected')

    def __repr__(self):
        return str(self.__dict__)


class ClientMessage(BaseMessage):
    def __init__(self, game_data: GameData = None, command: Command = None,
                 status: Status = None, additional_info=None):
        self.command = command
        self.status = status
        self.additional_info = additional_info
        self.game_data = game_data


class ServerReply(BaseMessage):
    def __init__(self, *game_data: GameData, command: Command = None,
                 status: Status = None, additional_info=None):
        self.command = command
        self.status = status
        self.additional_info = additional_info
        self.game_data_list = list(game_data)

    def append_game_data(self, *game_data: GameData):
        for data in game_data:
            self.game_data_list.append(data)
