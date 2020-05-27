import socket

from protocol import ServerReply

import logging.getLogger

from datetime import time


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = 'localhost'
        self.port = 5555
        self.addr = (self.server, self.port)
        reply = self.connect()
        print(reply.additional_info)

    def connect(self):
        try:
            self.client.connect(self.addr)
            return ServerReply.decode(self.client.recv(2048))
        except socket.error as e:
            print(e)

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)


if __name__ == '__main__':
    n = Network()
