# hw5

## Changes To Framework

### common.py

* `NUM_REPLICAS` constant has been moved from `server.py` to here.

### server.py

* Reorganized as a class
* Maintains a dictionary rather than a single data value by adding an optional `bin` field to READ/WRITE/UPDATE messages. 
* All UPDATEs are queued to simulate network latency. A background thread processes them at 5 second intervals.

### persistent_server.py 

Modified server that:

* Maintains a persistent connection to other replicas for sending UPDATEs
* Maintains a persistent connection to any connecting clients

### persistent_client.py

Modified client that:

* Maintains a persistent connection to a set of replicas
* Allows directing requests to specific replicas
* Optionally allows specifying a dictionary key to fetch

## Directories

All scripts in subdirectories assume that replicas run on ports `5000-5003`. To use a different range, run e.g. `sed -i 's/500/600/g' hw4/*`

### tests

This directory contains scripts that demonstrate the test cases described in the assignment.

In one window, run `bash tests/start_replicas.sh`, and in another run `python tests/1_basic_write.py` or one of the other python files.

### hw4

This directory contains scripts that attempt to reproduce the scenarios shown in HW4 Problem 6.

In order to use them, you must change `NUM_REPLICAS` in common.py from 3 to 4.

Then, in one window, run `bash hw4/start_replicas.sh`, and in another run `python hw4/1.py` or one of the other python files.

## Implementation Assumptions

* The server logs encountered exceptions, but does not attempt to recover from them.
* Several sockets are created with the assumption they don't go bad
* Clients can be trusted to send accurate context values

## Original README.txt

```
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
```