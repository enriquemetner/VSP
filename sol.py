from flask import Flask, request, jsonify

import socket
import datetime
import threading
import json

from consts import *

app = Flask(__name__)

class SOL:
    def __init__(self, com_uuid, star_uuid, sol_uuid, sol_ip, sol_tcp, status):
        self.com_uuid = com_uuid
        self.star_uuid = star_uuid
        self.sol_uuid = sol_uuid
        self.sol_ip = sol_ip
        self.sol_tcp = sol_tcp
        self.status = status
        self.star_integration_time = datetime.datetime.now()
        self.last_star_interaction_time = datetime.datetime.now()

        self.max_components = 4
        self.components = []
        self._add_component((self.com_uuid, self.sol_ip, self.sol_tcp, self.star_integration_time, self.last_star_interaction_time))

        self.start()

    def start(self):
        broadcast_listen_thread = threading.Thread(target=self.listen_for_hello)
        app_thread = threading.Thread(target=lambda: app.run(port=STARPORT))
        broadcast_listen_thread.start()
        app_thread.start()

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
                    "sol-ip": socket.gethostname(),
                    "sol-tcp": STARPORT,
                    "component": self.sol_uuid}
                response_data = json.dumps(response).encode('utf-8')
                sock.sendto(response_data, (address, 8014))
                print(f"Sent response to {address}")

    @app.route('/vs/v1/system/', methods=['POST'])
    def register_component(self):
        try:
            data = request.get_json()
            assert "star" in data and data["star"] == self.star_uuid
            assert "sol" in data and data["sol"] == self.sol_uuid
            assert "component" in data
            assert "com-ip" in data
            assert "com-tcp" in data and data["com-tcp"] == self.sol_tcp
            assert "status" in data
        except AssertionError:
            return jsonify({"status": "409 unauthorized"}), 409
        if len(self.components) > self.max_components:
            return jsonify({"status": "403 no room left"}), 403
        return jsonify({"status": "200 OK"}), 200

    def _add_component(self, data):
        self.components.append(data)
