from enum import Enum, auto


class ClientRole(Enum):
    HOST = auto()
    NON_HOST = auto()
    NOT_ASSIGNED = auto()

    def __repr__(self) -> str:
        return self.name


class Command(Enum):
    GET = auto()
    POST = auto()
    EXCHANGE = auto()

    JOIN_LOBBY = auto()
    IS_LOBBY_READY = auto()
    GET_LOBBY_PLAYERS = auto()
    LEAVE_LOBBY = auto()

    DISCONNECT = auto()

    def __repr__(self) -> str:
        return self.name


class Status(Enum):
    CONNECTION_SUCCESS = auto()
    IN_LOBBY_WAITING = auto()

    GAME_START = auto()
    LOBBY_PLAYER_DISCONNECTED = auto()

    COMMAND_SUCCESS = auto()
    COMMAND_FAIL = auto()

    BAD_COMMAND = auto()

    def __repr__(self) -> str:
        return self.name
