import requests

import socket
import json
import random
import datetime
import threading

from consts import *
from sol import SOL, app

class Component:


    def __init__(self):
        self.com_uuid = random.randint(1000, 9999)
        self.star_uuid = None
        self.sol_uuid = None
        self.sol_ip = None
        self.sol_tcp = None
        self.status = "active"
        self.star = None
        self.star_integration_time = None
        self.last_star_interaction_time = None

    @staticmethod
    def broadcast():
        print("Broadcasting 'HELLO?'")
        message = "HELLO?".encode('utf-8')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message, (BROADCAST_IP, STARPORT))
        sock.close()

    @staticmethod
    def await_response():
        print("Waiting for response")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 8014))
        sock.settimeout(3)
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            response = json.loads(data.decode('utf-8'))
            print(f"Received response from {addr}")
            return response
        except socket.timeout:
            print("No response received")
            return None
        finally:
            sock.close()

    def request_registration(self, response):
        url = f'http://{response["sol-ip"]}:{STARPORT}/vs/v1/system/'
        data = {
            'star': 'star-uuid',
            'sol': 'sol-uuid',
            'component': 'component-uuid',
            'com-ip': '192.168.1.1',
            'com-tcp': '8080',
            'status': 'active'
        }

        registration_response = requests.post(url, json=data)

        # Access the status code
        status_code = response.status_code
        print(f'Status Code: {status_code}')
        if status_code == 200:
            self.register(response)

    def register(self, response):
        pass


def start_component(component):
    print("Component started", component.com_uuid)
    response = None
    for _ in range(2):
        component.broadcast()
        response = component.await_response()
        if response:
            print("response received. Requesting registration")
            component.request_registration(response)
            break
    if not response:
        print("Becoming SOL")
        # this component becomes SOL. starting the broadcast listening thread and the flask app thread
        sol = SOL(component.com_uuid, component.star_uuid, component.sol_uuid, component.sol_ip, component.sol_tcp, component.status)
    else:
        print("Shutting down", component.com_uuid)

if __name__ == '__main__':
    component1 = Component()
    start_component(component1)

    component2 = Component()
    start_component(component2)
