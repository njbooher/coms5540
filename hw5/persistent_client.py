import json
import socket
from common import HOST, NUM_REPLICAS

class PersistentCausalClient:

    def __init__(self, *args):
        """Establish connections to replicas on provided list of ports"""
        if len(args) > NUM_REPLICAS:
            raise ValueError("PersistentCausalClient received too many ports")

        # we maintain a clock for all replicas
        self.context = [0 for i in range(NUM_REPLICAS)]

        # these are the ones we're actually going to connect to

        self.replica_connections = []

        for port in args:
            replica_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            replica_socket.settimeout(None)
            replica_socket.connect((HOST, port))
            self.replica_connections.append(replica_socket.makefile("rwb"))

    def update_context(self, timestamp):
        for i in range(NUM_REPLICAS):
            self.context[i] = max(self.context[i], timestamp[i])

    def send_message(self, replica, message):
        """Send one JSON request and return one JSON response."""

        payload = (json.dumps(message) + "\n").encode("utf-8")
        self.replica_connections[replica].write(payload)
        self.replica_connections[replica].flush()
        line = self.replica_connections[replica].readline()
        
        if not line:
            raise ConnectionError("Peer closed connection without a response.")

        response = json.loads(line.decode("utf-8"))
        if response.get("status") == "OK":
            print("Result:", response.get("value", ""))
            print("Timestamp:", response.get("timestamp"))
            if "timestamp" in response:
                self.update_context(response["timestamp"])
        else:
            print("Server response:", response)

        return response

    def read(self, replica, bin=None):
        if bin is not None:
            return self.send_message(replica, {"type": "READ", "bin": bin, "context": self.context.copy()})
        else:
            return self.send_message(replica, {"type": "READ", "context": self.context.copy()})

    def write(self, replica, value, bin=None):
        if bin is not None:
            self.send_message(replica, {"type": "WRITE", "bin": bin, "value": value, "context": self.context.copy()})
        else:
            self.send_message(replica, {"type": "WRITE", "value": value, "context": self.context.copy()})