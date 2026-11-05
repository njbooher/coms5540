Python starter framework — causal consistency

Start three servers in separate terminals, using the SAME ordered port list:

    python3 server.py 0 5000 5001 5002
    python3 server.py 1 5000 5001 5002
    python3 server.py 2 5000 5001 5002

You may choose ANY three distinct available TCP ports. The first server
argument is the replica ID (vector-clock index). The following three
arguments are the ports for replica IDs 0, 1, and 2, respectively.

Start one or more independent clients:

    python3 client.py

Client prompts:
    Your command (R - Read, W x - Append x to string):
    Which replica to contact (input the port number of the replica):

For invalid/unreachable/non-replica ports, the client asks again.
The HELLO probe verifies that the destination speaks the starter
framework protocol and identifies itself as replica 0, 1, or 2.
It does NOT authenticate membership in a particular three-replica group.
No registry or hard-coded REPLICAS dictionary is required by the client.

Examples: R, W A, W hello world, Q

Files:
    common.py: provided TCP/JSON utilities.
    client.py: provided interactive client and causal-context tracking.
    server.py: provided socket/thread framework; students implement TODOs.

IMPORTANT: The server TODOs intentionally raise NotImplementedError.
Students must implement causal consistency before READ/WRITE/UPDATE work.
