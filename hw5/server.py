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

from common import (
    HOST,
    receive_json_line,
    send_json_line,
    send_message,
)

NUM_REPLICAS = 3

if len(sys.argv) != 5:
    print("Usage: python3 server.py <replica_id> <port0> <port1> <port2>")
    sys.exit(1)

try:
    replica_id = int(sys.argv[1])
    ports = [int(p) for p in sys.argv[2:5]]
    if replica_id not in (0, 1, 2):
        raise ValueError("Replica ID must be 0, 1, or 2")
    if any(not 1 <= p <= 65535 for p in ports) or len(set(ports)) != 3:
        raise ValueError("Ports must be distinct integers between 1 and 65535")
except ValueError as exc:
    print(f"Invalid arguments: {exc}")
    sys.exit(1)

my_port = ports[replica_id]


def send_to_peer(peer_id, update):
    """Send an UPDATE to a peer; receipt acknowledgement is not delivery."""
    if peer_id == replica_id or peer_id not in (0, 1, 2):
        raise ValueError("Invalid peer ID")
    return send_message(HOST, ports[peer_id], update)


# ----------------------------------------------------------------------
# Shared replica state
# ----------------------------------------------------------------------

data = ""
vector_clock = [0, 0, 0]

# Each entry should contain:
# {
#     "type": "UPDATE",
#     "value": ...,
#     "timestamp": [x, y, z],
#     "origin": ...
# }
pending_updates = []

# Condition includes a lock. Use it to protect the three shared variables
# above and to wait/notify when the vector clock changes.
condition = threading.Condition()


# ----------------------------------------------------------------------
# Vector-clock / causal-consistency functions
# Students implement these functions.
# ----------------------------------------------------------------------

def clock_ge(clock_a, clock_b):
    """
    Return True iff clock_a >= clock_b component-wise.

    TODO: implement.
    """
    raise NotImplementedError


def can_apply_update(timestamp, origin):
    """
    Return True iff an UPDATE with the given timestamp and origin is
    causally ready at this replica.

    This function is called while 'condition' is held.

    TODO: implement the causal-delivery test from the assignment.
    """
    raise NotImplementedError


def apply_update(update):
    """
    Apply an UPDATE that is already known to be causally ready.

    This function is called while 'condition' is held.

    TODO:
      1. Append update["value"] to data.
      2. Update the appropriate vector-clock component.
      3. Do NOT create another UPDATE; this write originated elsewhere.
    """
    raise NotImplementedError


def check_pending_updates():
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

def handle_read(message):
    """
    Expected request:
        {
            "type": "READ",
            "context": [c0, c1, c2]
        }

    TODO:
      * wait until vector_clock >= client context
      * return current data and a COPY of vector_clock
    """
    raise NotImplementedError


def handle_write(message):
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
      3. Increment vector_clock[replica_id].
      4. Make a COPY of the resulting timestamp.
      5. Construct an UPDATE message.
      6. Release the condition lock before network communication.
      7. Propagate the UPDATE to both peer replicas.
      8. Return the local value and timestamp to the client.

    The originating replica does not need to wait for a peer UPDATE to
    become causally applicable. The peer acknowledges receipt/buffering.
    """
    raise NotImplementedError


def handle_update(message):
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


def handle_request(message):
    """Dispatch a decoded request."""
    msg_type = message.get("type")

    if msg_type == "HELLO":
        return {"status": "OK", "replica_id": replica_id}
    if msg_type == "READ":
        return handle_read(message)
    if msg_type == "WRITE":
        return handle_write(message)
    if msg_type == "UPDATE":
        return handle_update(message)

    return {"status": "ERROR", "message": "Unknown request type"}


# ----------------------------------------------------------------------
# Provided TCP server framework
# Students normally should NOT need to modify code below this line.
# ----------------------------------------------------------------------

def serve_connection(conn, addr):
    try:
        stream = conn.makefile("rwb")
        message = receive_json_line(stream)

        if message is None:
            return

        print(f"[R{replica_id}] received from {addr}: {message}")
        response = handle_request(message)
        send_json_line(stream, response)

    except NotImplementedError as exc:
        print(
            f"[R{replica_id}] Request handler not implemented: "
            f"{type(exc).__name__}: {exc}"
        )

    except Exception as exc:
        print(
            f"[R{replica_id}] Error processing request from {addr}: "
            f"{type(exc).__name__}: {exc}"
        )

    #except Exception as exc:
    #    print(f"[R{replica_id}] connection error from {addr}: {exc}")
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


def run_server():
    host, port = HOST, my_port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen()

        print(f"Replica {replica_id} started")
        print(f"Listening on {host}:{port}")
        print(f'Data: "{data}"')
        print(f"Clock: {vector_clock}")

        while True:
            conn, addr = server_sock.accept()
            thread = threading.Thread(
                target=serve_connection,
                args=(conn, addr),
                daemon=True,
            )
            thread.start()


if __name__ == "__main__":
    run_server()
