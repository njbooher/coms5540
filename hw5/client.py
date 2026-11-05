"""
Provided interactive client for the causal-consistency assignment.

Start: python3 client.py

Commands: R (read), W x (append text x), Q (quit).
The destination port is requested separately for each operation.

With arbitrary server ports, a port is accepted only after a server
responds to a HELLO request with a valid replica identity.
"""
from common import HOST, send_message

context = [0, 0, 0]


def update_context(timestamp):
    for i in range(3):
        context[i] = max(context[i], timestamp[i])


def prompt_operation():
    while True:
        raw = input(
            "Your command (R - Read, W x - Append x to string): "
        )
        stripped = raw.strip()
        if stripped.upper() == "Q":
            return None
        if stripped.upper() == "R":
            return {"type": "READ", "context": context.copy()}
        if len(raw) >= 3 and raw[0].upper() == "W" and raw[1].isspace():
            value = raw[2:]
            if value:
                return {
                    "type": "WRITE",
                    "value": value,
                    "context": context.copy(),
                }
        print("Invalid command. Enter R, W x, or Q.")


def prompt_port():
    prompt = "Which replica to contact (input the port number of the replica): "
    while True:
        raw = input(prompt).strip()
        try:
            port = int(raw)
            if not 1 <= port <= 65535:
                raise ValueError("Out of range")
            response = send_message(
                HOST, port, {"type": "HELLO"}, timeout=2
            )
            if (
                response.get("status") == "OK"
                and type(response.get("replica_id")) is int
                and response["replica_id"] in (0, 1, 2)
            ):
                return port
        except (ValueError, OSError, TimeoutError, EOFError):
            pass
        except (KeyError, TypeError, AttributeError):
            pass
        prompt = "The provided port number is invalid; please provide a valid one: "


def main():
    print("Causal-consistency client (Q to quit)")
    while True:
        try:
            request = prompt_operation()
            if request is None:
                return
            port = prompt_port()
            # No client timeout: a causally blocked READ/WRITE may need to wait.
            response = send_message(HOST, port, request)
            if response.get("status") == "OK":
                print("Result:", response.get("value", ""))
                print("Timestamp:", response.get("timestamp"))
                if "timestamp" in response:
                    update_context(response["timestamp"])
            else:
                print("Server response:", response)
        except (KeyboardInterrupt, EOFError):
            print()
            return
        except (OSError, ValueError) as exc:
            print("Request failed:", exc)
            # Keep the causal context unchanged on a failed request.


if __name__ == "__main__":
    main()
