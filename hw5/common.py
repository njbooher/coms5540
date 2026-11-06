"""
common.py

Provided communication utilities for the causal-consistency assignment.

This file handles:
  * TCP/JSON request-response communication
  * JSON encoding/decoding
  * TCP message framing (one JSON object per line)
  * sending a request and receiving one response

Students normally should NOT need to modify this file.
"""

import json
import socket

HOST = "127.0.0.1"
NUM_REPLICAS = 3

def send_message(host, port, message, timeout=None):
    """Send one JSON request and return one JSON response."""
    with socket.create_connection((host, port), timeout=timeout) as sock:
        stream = sock.makefile("rwb")
        payload = (json.dumps(message) + "\n").encode("utf-8")
        stream.write(payload)
        stream.flush()

        line = stream.readline()
        if not line:
            raise ConnectionError("Peer closed connection without a response.")

        return json.loads(line.decode("utf-8"))



def receive_json_line(stream):
    """Read one newline-delimited JSON object from a binary stream."""
    line = stream.readline()
    if not line:
        return None
    return json.loads(line.decode("utf-8"))


def send_json_line(stream, message):
    """Write one newline-delimited JSON object to a binary stream."""
    stream.write((json.dumps(message) + "\n").encode("utf-8"))
    stream.flush()
