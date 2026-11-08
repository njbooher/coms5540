import socket
import sys
import json
import argparse

from common import (
    HOST,
    NUM_REPLICAS,
    receive_json_line,
    send_json_line,
)

from server import CausalServer

class PersistentCausalServer(CausalServer):

    def __init__(self, replica_id, ports):
        super(PersistentCausalServer, self).__init__(replica_id, ports)

        self.replica_connections = [None for i in range(NUM_REPLICAS)]

    def broadcast_write(self, update):
        """Send an UPDATE to all peers; receipt acknowledgement is not delivery."""
        update['origin'] = self.replica_id
        for peer_id in range(NUM_REPLICAS):

            if peer_id == self.replica_id:
                continue

            if self.replica_connections[peer_id] is None:
                repl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                repl_socket.settimeout(None)
                repl_socket.connect((HOST, self.ports[peer_id]))
                self.replica_connections[peer_id] = repl_socket.makefile("rwb")

            line = ""
            payload = (json.dumps(update) + "\n").encode("utf-8")
            self.replica_connections[peer_id].write(payload)
            self.replica_connections[peer_id].flush()
            line = self.replica_connections[peer_id].readline()
            
            if not line:
                raise ConnectionError("Peer closed connection without a response.")

    def serve_connection(self, conn, addr):

        print(f"[R{self.replica_id}] started persistent connection with {addr}")

        with conn.makefile("rwb") as stream:

            while True:
                try:
                    message = receive_json_line(stream)

                    if message is None:
                        continue

                    print(f"[R{self.replica_id}] received from {addr}: {message}")
                    response = self.handle_request(message)
                    send_json_line(stream, response)

                except NotImplementedError as exc:
                    print(
                        f"[R{self.replica_id}] Request handler not implemented: "
                        f"{type(exc).__name__}: {exc}"
                    )

                except Exception as exc:
                    print(
                        f"[R{self.replica_id}] Error processing request from {addr}: "
                        f"{type(exc).__name__}: {exc}"
                    )

                #except Exception as exc:
                #    print(f"[R{self.replica_id}] connection error from {addr}: {exc}")
                    try:
                        send_json_line(
                            stream,
                            {"status": "ERROR", "message": str(exc)}
                        )
                    except Exception:
                        print(
                            f"[R{self.replica_id}] Error notifying client {addr} about error: "
                            f"{type(exc).__name__}: {exc}"
                            )

def main():
    parser = argparse.ArgumentParser(
                        prog='server.py',
                        description='Server providing causal-consistency')
    parser.add_argument('replica_id', type=int, choices=range(NUM_REPLICAS))
    parser.add_argument('replica_port', type=int, nargs=NUM_REPLICAS)
    args = parser.parse_args()

    try:
        if (any(not 1 <= p <= 65535 for p in args.replica_port) or len(set(args.replica_port)) < NUM_REPLICAS):
            raise ValueError("Ports must be distinct integers between 1 and 65535")
    except ValueError as exc:
        print(f"Invalid arguments: {exc}")
        sys.exit(1)

    server = PersistentCausalServer(args.replica_id, args.replica_port)
    server.run_server()

if __name__ == "__main__":
    main()