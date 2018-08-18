#!/bin/bash
# Stop the PAKET servers (or any python servers listening on same ports).

[ "$1" ] || "$0" 5000 5001 5002
while [ "$1" ]; do
    pid=$(netstat -lntp | grep -F "0.0.0.0:$1 " | grep -Po '\d*(?=/)')
    [ "$pid" ] && kill $pid || echo "no process listening on port $1"
    shift
done
