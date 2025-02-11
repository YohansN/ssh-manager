import hashlib

class SSHConnection: #Model to store ssh connections
    def __init__(self, connection_name: str = "", connection_key: str = "", connection_description: str = ""):
        self.connection_name = connection_name if connection_name else connection_key
        self.connection_key = connection_key
        self.connection_description = connection_description
        self.connection_user = connection_key.split("@")[0]
        self.connection_host = connection_key.split("@")[1]
        self.connection_id = hashlib.sha256(f"{connection_name}-{connection_key}-{self.connection_user}-{self.connection_host}-{connection_description}".encode()).hexdigest()
