import requests

import socket
import json
import random

from consts import *

class Component:
    def __init__(self):
        self.com_uuid = int(random.randint(0, 9000) + 1000)
        self.star = None
        self.sol = None
        self.sol_ip = None
        self.sol_tcp = None
        self.status = "active"
        self.start()

    def start(self):
        for _ in range(2):
            self.broadcast()
            response = self.await_response()
            if response:
                self.request_registration(response)
                if response.status_code == 200:
                    self.register(response)
                else:
                    print(f"Failed to register with Star-{response['star']}")
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

    def request_registration(self, response):
        url = f"http://{response["sol-ip"]}:{response["sol-tcp"]}/vs/v1/system"
        headers = {'Content-Type': 'application/json'}
        post_data = {
            "star": response['star'],
            "sol": response['sol'],
            "component": self.com_uuid,
            "com_ip": socket.gethostname(),
            "com_tcp": STARPORT,
            "status": self.status
        }
        response = requests.post(url, headers=headers, data=json.dumps(post_data))
        return response.status_code, response.text


    def register(self, response):
        self.star = response['star']
        self.sol = response['sol']
        self.sol_ip = response['sol_ip']
        self.sol_tcp = response['sol_tcp']
        assert self.com_uuid == response['com_uuid']








    def init_star(self):
        pass