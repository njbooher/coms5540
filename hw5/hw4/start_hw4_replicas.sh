# you must manually change NUM_REPLICAS in common.py for this to work
tmux \
    new-session  'python persistent_server.py 0 5000 5001 5002 5003' \; \
    split-window -h 'python persistent_server.py 1 5000 5001 5002 5003' \; \
    split-window -h 'python persistent_server.py 2 5000 5001 5002 5003' \; \
    split-window -h 'python persistent_server.py 3 5000 5001 5002 5003'