import socket
from typing import Optional

from common import ServerConfig
from networking import GameClient
from logger import Logger


class GameServer:

    def __init__(self, server_ip: str, server_port: int, allowed_max_connection: Optional[int] = None):
        self._logger = Logger(self.__class__.__name__)
        self._address = (server_ip, server_port)
        self._max_connection = allowed_max_connection

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        try:
            self._server_socket.bind(self._address)
        except socket.error as e:
            print(e)
        else:
            if self._max_connection:
                self._server_socket.listen(ServerConfig.MAX_CONNECTION)
            else:
                self._server_socket.listen()
            self._logger.info(f'Server started at {self._address} !!!')
            self._logger.debug('Waiting for connection...')
            self._wait_for_connection()

    def _wait_for_connection(self):
        while True:
            client_conn, client_addr = self._server_socket.accept()
            _client = GameClient(client_conn, client_addr)
            _client.start_client_connection()
