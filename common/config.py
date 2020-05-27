import socket


class ServerConfig:
    HOSTNAME = socket.gethostname()
    IP_ADDRESS = socket.gethostbyname(HOSTNAME)
    PORT = 5555
    MAX_CONNECTION = 2
    MAX_LOBBY_PLAYER = 2


class ClientConfig:
    RECEIVE_BUFFER_SIZE = 2048
    MAX_DATA_QUEUE_SIZE = 1000
