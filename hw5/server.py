"""
server.py

Starter server framework for the causal-consistency assignment.

Usage:
    python3 server.py 0 5000 5001 5002
    python3 server.py 1 5000 5001 5002
    python3 server.py 2 5000 5001 5002

The socket/threading framework is provided. Students implement the causal
consistency logic in the TODO sections.

Important shared state:
    data
    vector_clock
    pending_updates

A threading.Condition is provided both to protect shared state and to let
READ/WRITE operations sleep while waiting for causal dependencies.
"""

import socket
import sys
import threading
import argparse

from common import (
    HOST,
    NUM_REPLICAS,
    receive_json_line,
    send_json_line,
    send_message,
)

def clock_ge(clock_a, clock_b):
    """
    Return True iff clock_a >= clock_b component-wise.

    TODO: implement.
    """
    if len(clock_a) != len(clock_b):
        raise ValueError("clock_ge was provided invalid clocks")

    for i in range(len(clock_a)):
        if clock_a[i] < clock_b[i]:
            return False

    return True

class CausalServer:

    def __init__(self, replica_id, ports):

        self.replica_id = replica_id
        self.ports = ports
        self.my_port = self.ports[self.replica_id]

        # ----------------------------------------------------------------------
        # Shared replica state
        # ----------------------------------------------------------------------

        self.data = ""
        self.vector_clock = [0, 0, 0]

        # Each entry should contain:
        # {
        #     "type": "UPDATE",
        #     "value": ...,
        #     "timestamp": [x, y, z],
        #     "origin": ...
        # }
        self.pending_updates = []

        # Condition includes a lock. Use it to protect the three shared variables
        # above and to wait/notify when the vector clock changes.
        self.condition = threading.Condition()

    def send_to_peer(self, peer_id, update):
        """Send an UPDATE to a peer; receipt acknowledgement is not delivery."""
        if peer_id == self.replica_id or peer_id not in (0, 1, 2):
            raise ValueError("Invalid peer ID")
        return send_message(HOST, self.ports[peer_id], update)

    # ----------------------------------------------------------------------
    # Vector-clock / causal-consistency functions
    # Students implement these functions.
    # ----------------------------------------------------------------------

    def can_apply_update(self, timestamp, origin):
        """
        Return True iff an UPDATE with the given timestamp and origin is
        causally ready at this replica.

        This function is called while 'condition' is held.

        TODO: implement the causal-delivery test from the assignment.
        """
        raise NotImplementedError


    def apply_update(self, update):
        """
        Apply an UPDATE that is already known to be causally ready.

        This function is called while 'condition' is held.

        TODO:
        1. Append update["value"] to data.
        2. Update the appropriate vector-clock component.
        3. Do NOT create another UPDATE; this write originated elsewhere.
        """
        raise NotImplementedError


    def check_pending_updates(self):
        """
        Repeatedly examine pending_updates and apply any update that has become
        causally ready. Continue until no additional update can be applied.

        This function is called while 'condition' is held.

        TODO: implement.
        """
        raise NotImplementedError


    # ----------------------------------------------------------------------
    # Request handlers
    # Students implement the causal-consistency behavior here.
    # ----------------------------------------------------------------------

    def handle_read(self, message):
        """
        Expected request:
            {
                "type": "READ",
                "context": [c0, c1, c2]
            }
        """
        with self.condition:
            self.condition.wait_for(lambda: clock_ge(self.vector_clock, message['context']))
            return {'status': 'OK', 'value': self.data, 'timestamp': self.vector_clock.copy()}


    def handle_write(self, message):
        """
        Expected request:
            {
                "type": "WRITE",
                "value": "A",
                "context": [c0, c1, c2]
            }

        TODO:
        1. Wait until local vector_clock >= client context.
        2. Append value to local data.
        3. Increment self.vector_clock[self.replica_id].
        4. Make a COPY of the resulting timestamp.
        5. Construct an UPDATE message.
        6. Release the condition lock before network communication.
        7. Propagate the UPDATE to both peer replicas.
        8. Return the local value and timestamp to the client.

        The originating replica does not need to wait for a peer UPDATE to
        become causally applicable. The peer acknowledges receipt/buffering.
        """
        raise NotImplementedError


    def handle_update(self, message):
        """
        Expected request:
            {
                "type": "UPDATE",
                "value": "A",
                "timestamp": [t0, t1, t2],
                "origin": 0
            }

        TODO:
        * if causally ready, apply the UPDATE and then recheck pending updates
        * otherwise, put the UPDATE in pending_updates
        * notify waiting READ/WRITE threads if vector_clock advanced

        Return an acknowledgement after the UPDATE has been received and either
        applied or safely buffered. The acknowledgement does NOT mean that a
        buffered update has already been applied.
        """
        raise NotImplementedError


    def handle_request(self, message):
        """Dispatch a decoded request."""
        msg_type = message.get("type")

        if msg_type == "HELLO":
            return {"status": "OK", "replica_id": self.replica_id}
        if msg_type == "READ":
            return self.handle_read(message)
        if msg_type == "WRITE":
            return self.handle_write(message)
        if msg_type == "UPDATE":
            return self.handle_update(message)

        return {"status": "ERROR", "message": "Unknown request type"}


    # ----------------------------------------------------------------------
    # Provided TCP server framework
    # Students normally should NOT need to modify code below this line.
    # ----------------------------------------------------------------------

    def serve_connection(self, conn, addr):
        try:
            stream = conn.makefile("rwb")
            message = receive_json_line(stream)

            if message is None:
                return

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
                stream = conn.makefile("rwb")
                send_json_line(
                    stream,
                    {"status": "ERROR", "message": str(exc)}
                )
            except Exception:
                pass
        finally:
            conn.close()


    def run_server(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_sock.bind((HOST, self.my_port))
            server_sock.listen()

            print(f"Replica {self.replica_id} started")
            print(f"Listening on {HOST}:{self.my_port}")
            print(f'Data: "{self.data}"')
            print(f"Clock: {self.vector_clock}")

            while True:
                conn, addr = server_sock.accept()
                thread = threading.Thread(
                    target=self.serve_connection,
                    args=(conn, addr),
                    daemon=True,
                )
                thread.start()


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

    server = CausalServer(args.replica_id, args.replica_port)
    server.run_server()

if __name__ == "__main__":
    main()
    
