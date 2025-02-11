import hashlib

class SSHKey: #Model to store ssh keys
    def __init__(self, key_path: str, key_name: str = "", key_type: str = "", key_description: str = ""):
        self.key_path = key_path
        self.key_name = key_name if key_name else key_path.split("/")[-1]
        self.key_type = key_type if key_type else key_path.split(".")[-1]
        self.key_description = key_description
        self.key_id = hashlib.sha256(key_path.encode()).hexdigest()
