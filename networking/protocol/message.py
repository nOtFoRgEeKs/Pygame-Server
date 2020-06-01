from __future__ import annotations

import pickle

from networking.protocol import Command, Status


class BaseMessage:
    @classmethod
    def encode(cls, message: BaseMessage) -> bytes:
        if not isinstance(message, cls):
            raise TypeError(f'Expected: {cls.__name__} Received: {type(message)}')
        else:
            return pickle.dumps(message)

    @classmethod
    def decode(cls, stream: bytes) -> BaseMessage:
        object_ = pickle.loads(stream)
        if isinstance(object_, cls):
            return object_
        else:
            raise TypeError(f'Expected: {cls.__name__} Received: {type(object_)}')

    def __repr__(self):
        return str(self.__dict__)


class ClientMessage(BaseMessage):
    def __init__(self, data: bytes = None, command: Command = None,
                 status: Status = None, additional_info=None):
        self.command = command
        self.status = status
        self.additional_info = additional_info
        self.data = data


class ServerReply(BaseMessage):
    def __init__(self, *data: bytes, command: Command = None,
                 status: Status = None, additional_info=None):
        self.command = command
        self.status = status
        self.additional_info = additional_info
        self.data_list = list(data)

    def append_data(self, *data: bytes):
        for data_ in data:
            self.data_list.append(data_)
