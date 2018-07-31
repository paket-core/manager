#!/bin/bash
# Run the PAKET servers.

. paket.env

for server in "${PAKET_SERVERS[@]}"; do
    cmd="python routes.py"
    if [ "$TMUX" ]; then
        cmd="tmux split-pane -d $cmd"
    fi
    cmd="$cmd"
    pushd "../$server"
    $cmd &
    popd
done
