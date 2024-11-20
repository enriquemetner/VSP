from flask import Flask

import socket
import json
import random
import datetime
import threading

from consts import *
from star import Star

class Component:


    def __init__(self):
        self.com_uuid = int(random.randint(0, 9000) + 1000)
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
        sock.bind(('', STARPORT))
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

    def listen_for_hello(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', STARPORT))
        while True:
            data, (address, port) = sock.recvfrom(1024)
            message = data.decode('utf-8').strip('\x00')
            print(f"Received message: {message} from {address}")
            # Check if the message is "HELLO?"
            if message == "HELLO?":
                # Respond with the star information
                response = {
                    "star": self.star_uuid,
                    "sol": self.sol_uuid,
                    "sol-ip": self.sol_ip,
                    "sol-tcp": STARPORT,
                    "component": self.sol_uuid}
                response_data = json.dumps(response).encode('utf-8')
                sock.sendto(response_data, (address, STARPORT))
                print(f"Sent response to {address}")

    def init_star(self):
        self.star = Star(self.sol_uuid, self.sol_ip, TEAM_ID)
        self.star_integration_time = datetime.datetime.now()
        self.last_star_interaction_time = datetime.datetime.now()

    def request_registration(self, response):
        pass

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
        print("Creating a new Star")
        component.init_star()
        listen_thread = threading.Thread(target=component.listen_for_hello)
        listen_thread.start()
    else:
        print("Shutting down", component.com_uuid)

if __name__ == '__main__':
    component = Component()
    start_component(component)

    component2 = Component()
    start_component(component2)
