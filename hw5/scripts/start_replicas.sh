tmux \
    new-session  'python persistent_server.py 0 5000 5001 5002' \; \
    split-window 'python persistent_server.py 1 5000 5001 5002' \; \
    split-window 'python persistent_server.py 2 5000 5001 5002'