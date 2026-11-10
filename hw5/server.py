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
import time

from collections import defaultdict

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

        self.data = defaultdict(str)
        self.default_data_bin = 'x'
        self.vector_clock = [0 for i in range(NUM_REPLICAS)]

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

    def broadcast_write(self, update):
        """Send an UPDATE to all peers; receipt acknowledgement is not delivery."""
        update['origin'] = self.replica_id
        for peer_id in range(NUM_REPLICAS):
            if peer_id == self.replica_id:
                continue
            send_message(HOST, self.ports[peer_id], update)

    # ----------------------------------------------------------------------
    # Vector-clock / causal-consistency functions
    # Students implement these functions.
    # ----------------------------------------------------------------------

    def can_apply_update(self, timestamp, origin):
        """
        Return True iff an UPDATE with the given timestamp and origin is
        causally ready at this replica.

        This function is called while 'condition' is held.
        """

        if self.vector_clock[origin] != (timestamp[origin] - 1):
            return False

        for i in range(NUM_REPLICAS):
            if i == origin:
                continue
            if timestamp[i] > self.vector_clock[i]:
                return False
        
        return True

    def apply_update(self, update):
        """
        Apply an UPDATE that is already known to be causally ready.

        This function is called while 'condition' is held.
        """

        data_bin = self.default_data_bin if 'bin' not in update else update['bin']
        print(f"[R{self.replica_id}]: applying update, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {update['timestamp']}")
        self.data[data_bin] += update['value']
        self.vector_clock[update['origin']] = update['timestamp'][update['origin']]
        print(f"[R{self.replica_id}]: applied update, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {update['timestamp']}")
        self.condition.notify_all()

    def check_pending_updates(self):
        """
        Repeatedly examine pending_updates and apply any update that has become
        causally ready. Continue until no additional update can be applied.

        This function is called while 'condition' is held.
        """

        applied_update = True
        while applied_update:
            applied_update = False
            for update in self.pending_updates:
                if self.can_apply_update(update['timestamp'], update['origin']):
                    self.apply_update(update)
                    applied_update = True

    def background_check_pending_updates(self):
        while True:
            time.sleep(5)
            with self.condition:
                self.check_pending_updates()

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

        data_bin = self.default_data_bin if 'bin' not in message else message['bin']
        print(f"[R{self.replica_id}]: handling read, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {message['context']}")
        with self.condition:
            self.condition.wait_for(lambda: clock_ge(self.vector_clock, message['context']))
            print(f"[R{self.replica_id}]: handling read, finished waiting, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {message['context']}")
            return {'status': 'OK', 'value': self.data[data_bin], 'timestamp': self.vector_clock.copy()}


    def handle_write(self, message):
        """
        Expected request:
            {
                "type": "WRITE",
                "value": "A",
                "context": [c0, c1, c2]
            }
        """

        data_bin = self.default_data_bin if 'bin' not in message else message['bin']

        update_message = {
            'type': 'UPDATE',
            'bin': data_bin
        }

        print(f"[R{self.replica_id}]: handling write, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {message['context']}")

        with self.condition:
            self.condition.wait_for(lambda: clock_ge(self.vector_clock, message['context']))
            print(f"[R{self.replica_id}]: handling write, finished waiting, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {message['context']}")
            self.data[data_bin] += message['value']
            update_message['value'] = message['value']
            self.vector_clock[self.replica_id] += 1
            update_message['timestamp'] = self.vector_clock.copy()
            print(f"[R{self.replica_id}]: handling write, applied write, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {message['context']}")
            self.condition.notify_all()

        """
        The originating replica does not need to wait for a peer UPDATE to
        become causally applicable. The peer acknowledges receipt/buffering.
        """
        self.broadcast_write(update_message)

        return {'status': 'OK', 'value': update_message['value'], 'timestamp': update_message['timestamp']}


    def handle_update(self, message):
        """
        Expected request:
            {
                "type": "UPDATE",
                "value": "A",
                "timestamp": [t0, t1, t2],
                "origin": 0
            }
        """

        data_bin = self.default_data_bin if 'bin' not in message else message['bin']

        with self.condition:
            print(f"[R{self.replica_id}]: queuing update, my clock: {self.vector_clock}, bin: {data_bin}, my data: {self.data[data_bin]}, message context: {message['timestamp']}")
            self.pending_updates.append(message)

        """
        Return an acknowledgement after the UPDATE has been received and either
        applied or safely buffered. The acknowledgement does NOT mean that a
        buffered update has already been applied.
        """

        return {'status': 'OK', 'value': message['value'], 'timestamp': message['timestamp']}


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

            updates_thread = threading.Thread(
                    target=self.background_check_pending_updates,
                    args=(),
                    daemon=True,
                )
            updates_thread.start()

            while True:
                conn, addr = server_sock.accept()
                thread = threading.Thread(
                    target=self.serve_connection,
                    args=(conn, addr),
                    daemon=True,
                )
                thread.start()


def main(server_class=CausalServer):
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

    server = server_class(args.replica_id, args.replica_port)
    server.run_server()

if __name__ == "__main__":
    main()
    
