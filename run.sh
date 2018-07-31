#!/bin/bash
# Run the PAKET servers.

. paket.env

if [ "$1" ]; then
    PYTHONPATH="..:../$1" ./venv/bin/python -m $1
else
    for server in "${PAKET_SERVERS[@]}"; do
    if [ "$TMUX" ]; then
        tmux split-pane -d "$0" $server
    else
        "$0" $server &
    fi
    done
fi
