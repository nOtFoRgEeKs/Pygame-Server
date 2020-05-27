from common import ServerConfig
from server import GameServer

if __name__ == '__main__':
    game_server = GameServer(server_ip=ServerConfig.IP_ADDRESS,
                             server_port=ServerConfig.PORT,
                             allowed_max_connection=ServerConfig.MAX_CONNECTION)
    game_server.start_server()
