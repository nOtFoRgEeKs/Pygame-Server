from __future__ import annotations

from typing import List, Dict

from common import UniqueId
from logger import Logger


class GameLobby:
    LOBBY_POOL: Dict[int, GameLobby] = dict()

    def __init__(self, max_player: int):
        self._logger = Logger(self.__class__.__name__)

        self._clients: List[int] = list()
        self._max_player: int = max_player
        self._id: int = UniqueId.generate()
        self._logger.tag = 'id:' + str(self._id)
        self._logger.info('New lobby created')

        GameLobby.LOBBY_POOL[self._id] = self

    @property
    def id(self) -> int:
        return self._id

    @property
    def clients(self) -> List[int]:
        return self._clients

    def has_space(self) -> bool:
        return len(self._clients) < self._max_player

    def add_client(self, client_id: int):
        self._clients.append(client_id)
        self._logger.info(f'Client {client_id} joined')

    def remove_client(self, client_id: int):
        self._clients.remove(client_id)
        self._logger.info(f'Client {client_id} left')

        if not len(self._clients):
            self.close_lobby()

    @staticmethod
    def find_empty():
        for lobby in GameLobby.LOBBY_POOL.values():
            if lobby.has_space():
                return lobby

    def close_lobby(self):
        self._logger.info('Closing lobby...')
        del GameLobby.LOBBY_POOL[self._id]
