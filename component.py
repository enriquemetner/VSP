import socket
import json
import random

from consts import *

class Component:
    def __init__(self):
        self.com_uuid = int(random.randint(0, 9000) + 1000)
        self.start()

    def start(self):
        for _ in range(2):
            self.broadcast()
            response = self.await_response()
            if response:
                self.register()
                return
        self.init_star()

    @staticmethod
    def broadcast():
        message = "HELLO?".encode('utf-8')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message, (BROADCAST_IP, STARPORT))
        sock.close()

    @staticmethod
    def await_response():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', STARPORT))
        sock.settimeout(10)
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            response = json.loads(data.decode('utf-8'))
            return response
        except socket.timeout:
            return None
        finally:
            sock.close()

    def register(self):
        pass

    def init_star(self):
        pass