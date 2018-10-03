#!/bin/bash
# Stop the PAKET servers (or any python servers listening on same ports).

. paket.env

[ "$1" ] || "$0" ${PAKET_ROUTER_PORT:-5000} ${PAKET_BRIDGE_PORT:-5001} ${PAKET_FUNDER_PORT:-5002}
while [ "$1" ]; do
    pid=$(netstat -lntp | grep -F "0.0.0.0:$1 " | grep -Po '\d*(?=/)')
    [ "$pid" ] && kill $pid || echo "no process listening on port $1"
    shift
done
