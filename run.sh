#!/bin/bash
# Run the PAKET servers.

. paket.env

if [ "$1" ]; then
    if [ "$FLASK_DEBUG" ]; then
        PYTHONPATH="..:../$1" ./venv/bin/python -m $1
    else
        PYTHONPATH="../$1" uwsgi -s "/tmp/$1.sock" --chmod-socket=664 --manage-script-name --mount /=__init__:APP
    fi
else
    for server in "${PAKET_SERVERS[@]}"; do
        if [ "$TMUX" ]; then
            tmux split-pane -dl5 "$0" $server
        else
            "$0" $server &
        fi
    done
fi
