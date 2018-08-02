#!/bin/bash
# Stop the PAKET servers.

if [ "$1" ]; then
    while [ "$1" ]; do
        kill $(netstat -lntp | grep -F "0.0.0.0:$1 " | grep -Po '\d*(?=/)')
        shift
    done
else
    "$0" 8000
    "$0" 8001
fi
