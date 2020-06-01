from __future__ import annotations

import socket
from queue import Queue
from threading import Lock
from typing import Dict, Optional, List

from common import ClientConfig, ServerUtils, ServerConfig, UniqueId
from logger import Logger
from networking import GameLobby
from networking.protocol import ClientMessage, ServerReply
from networking.protocol import ClientRole, Status, Command


class GameClient:
    CLIENT_POOL: Dict[int, GameClient] = dict()

    def __init__(self, connection: socket.socket, address: tuple):
        self._logger = Logger(self.__class__.__name__)

        self._conn: socket.socket = connection
        self._addr: tuple = address

        self._id: int = UniqueId.generate()
        self._logger.tag = 'id:' + str(self._id)
        self._logger.info(f'New connection from: {address}')

        self._in_lobby: bool = False
        self._lobby_id = None
        self._role: ClientRole = ClientRole.NOT_ASSIGNED
        self._running = False
        self._data_queue: Queue = Queue(maxsize=ClientConfig.MAX_DATA_QUEUE_SIZE)
        self._lock = Lock()

        GameClient.CLIENT_POOL[self._id] = self

    @ServerUtils.async_run
    def start_client_connection(self):
        if not self._send_success_message():
            self.stop_client_connection()
            return

        command_mapper = {
            Command.GET: self._dequeue_data,
            Command.POST: self._enqueue_data,
            Command.EXCHANGE: self._exchange_data,
            Command.JOIN_LOBBY: self._join_to_lobby,
            Command.IS_LOBBY_READY: self._find_lobby_ready,
            Command.GET_LOBBY_PLAYERS: self._who_in_lobby,
            Command.LEAVE_LOBBY: self._leave_from_lobby
        }

        self._running = True
        while self._running:
            received_msg: ClientMessage = self.receive_message()
            if not received_msg:
                break
            self._logger.debug('Received-> ', received_msg)

            if received_msg.command == Command.DISCONNECT:
                self._logger.info('Request to disconnect')
                break

            reply_msg = command_mapper[received_msg.command](received_msg)
            self._logger.debug('Sending-> ', reply_msg)
            if not self.send_message(reply_msg):
                break
        self.stop_client_connection()

    def stop_client_connection(self):
        self._logger.info(f'Client stopping {self._addr}')
        self._conn.close()

        if self._in_lobby:
            GameLobby.LOBBY_POOL[self._lobby_id].remove_client(self.id)

    def _join_to_lobby(self, received_msg: ClientMessage) -> ServerReply:
        self._logger.info('Request to join lobby')
        reply_msg = ServerReply()

        self.clear_data_queue()
        lobby = GameLobby.find_empty()
        if lobby:
            self._role = ClientRole.NON_HOST
            reply_msg.status = Status.GAME_START
        else:
            lobby = GameLobby(ServerConfig.MAX_LOBBY_PLAYER)
            self._role = ClientRole.HOST
            reply_msg.status = Status.IN_LOBBY_WAITING
        lobby.add_client(self._id)
        self._in_lobby = True
        self._lobby_id = lobby.id

        reply_msg.additional_info = self._role

        return reply_msg

    def _find_lobby_ready(self, received_msg: ClientMessage) -> ServerReply:
        reply_msg = ServerReply()
        if GameLobby.LOBBY_POOL[self._lobby_id].has_space():
            reply_msg.status = Status.IN_LOBBY_WAITING
        else:
            reply_msg.status = Status.GAME_START
        return reply_msg

    def _enqueue_data(self, received_msg: ClientMessage) -> ServerReply:
        # self._logger.info(f'Enqueue data: {received_msg.data}')
        reply_msg = ServerReply()
        if GameLobby.LOBBY_POOL[self._lobby_id].has_space():
            GameLobby.LOBBY_POOL[self._lobby_id].remove_client(self.id)
            reply_msg.status = Status.LOBBY_PLAYER_DISCONNECTED
            self._in_lobby = False
        else:
            self.push_data_queue(received_msg.data)
            reply_msg.status = Status.COMMAND_SUCCESS
        return reply_msg

    def _dequeue_data(self, received_msg: ClientMessage) -> ServerReply:
        # self._logger.info('Dequeue data')
        reply_msg = ServerReply()
        if GameLobby.LOBBY_POOL[self._lobby_id].has_space():
            GameLobby.LOBBY_POOL[self._lobby_id].remove_client(self.id)
            reply_msg.status = Status.LOBBY_PLAYER_DISCONNECTED
            self._in_lobby = False
        else:
            reply_msg.append_data(*self.pop_data_from_lobby_clients())
            reply_msg.status = Status.COMMAND_SUCCESS
        return reply_msg

    def _exchange_data(self, received_msg: ClientMessage) -> ServerReply:
        # self._logger.info(f'Enqueue data: {received_msg.data}')
        reply_msg = ServerReply()
        if GameLobby.LOBBY_POOL[self._lobby_id].has_space():
            GameLobby.LOBBY_POOL[self._lobby_id].remove_client(self.id)
            reply_msg.status = Status.LOBBY_PLAYER_DISCONNECTED
            self._in_lobby = False
        else:
            self.push_data_queue(received_msg.data)
            reply_msg.append_data(*self.pop_data_from_lobby_clients())
            reply_msg.status = Status.COMMAND_SUCCESS
        return reply_msg

    def _leave_from_lobby(self, received_msg: ClientMessage) -> ServerReply:
        self._logger.info('Request to leave lobby')
        if self._in_lobby:
            GameLobby.LOBBY_POOL[self._lobby_id].remove_client(self.id)
            return ServerReply(status=Status.COMMAND_SUCCESS)
        return ServerReply(status=Status.BAD_COMMAND)

    def _who_in_lobby(self, received_msg: ClientMessage) -> ServerReply:
        reply_msg = ServerReply()

        return reply_msg

    @property
    def id(self) -> int:
        return self._id

    @property
    def role(self) -> ClientRole:
        return self._role

    def clear_data_queue(self):
        with self._lock:
            self._data_queue.queue.clear()

    def push_data_queue(self, data: bytes):
        with self._lock:
            self._data_queue.put_nowait(data)

    def pop_data_queue(self) -> bytes:
        with self._lock:
            data = self._data_queue.get_nowait()
        return data

    def pop_data_from_lobby_clients(self) -> List[bytes]:
        return [GameClient.CLIENT_POOL[client_id].pop_data_queue() for client_id in
                GameLobby.LOBBY_POOL[self._lobby_id].clients if
                client_id != self._id and not GameClient.CLIENT_POOL[client_id].is_data_queue_empty()]

    def is_data_queue_empty(self) -> bool:
        with self._lock:
            empty = self._data_queue.empty()
        return empty

    def send_message(self, message: ServerReply) -> bool:
        try:
            data_bytes = ServerReply.encode(message)
            self._conn.sendall(data_bytes)
        except socket.error:
            self._logger.exception('Unable to send data...')
            self._logger.warning(f'Lost client connection: {self._addr}')
            return False
        else:
            return True

    def receive_message(self) -> Optional[ClientMessage]:
        try:
            data_bytes: bytes = self._conn.recv(ClientConfig.RECEIVE_BUFFER_SIZE)
            if len(data_bytes) == 0:
                self._logger.warning(f'Lost client connection: {self._addr}')
                return
        except socket.error:
            self._logger.exception('Unable to receive data...')
            return
        else:
            return ClientMessage.decode(data_bytes)

    def _send_success_message(self) -> bool:
        msg = ServerReply(additional_info=self._id, status=Status.CONNECTION_SUCCESS)
        return self.send_message(msg)

    def __del__(self):
        if self._in_lobby:
            GameLobby.LOBBY_POOL[self._lobby_id].remove_client(self._id)

        del GameClient.CLIENT_POOL[self._id]
