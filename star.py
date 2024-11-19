import hashlib
import datetime

class Star:
    def __init__(self, sol_uuid, sol_ip, team_id, max_components=4):
        self.sol_uuid = sol_uuid
        self.sol_ip = sol_ip
        self.team_id = team_id
        self.star_uuid = self.generate_star_uuid()
        self.init_time = datetime.datetime.now()
        self.components = [sol_uuid]
        self.max_components = max_components

    def generate_star_uuid(self):
        data = f"{self.sol_ip}{self.team_id}{self.sol_uuid}".encode()
        return hashlib.md5(data).hexdigest()