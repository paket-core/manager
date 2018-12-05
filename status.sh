#!/bin/bash
# List git status of PAKET servers.

. paket.env

for server in "${PAKET_SERVERS[@]}"; do
    echo "$server: $(git -C "../$server" rev-parse HEAD) $(git -C "../$server" symbolic-ref HEAD)"
    while read requirement; do
        if [ "${requirement:0:3}" = '../' ]; then
            echo "${requirement:3}: $(git -C "$requirement" rev-parse HEAD)"
        fi
    done < "../$server/requirements.txt"
done | sort -u | column -t
