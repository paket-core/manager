#!/bin/bash
# Initialize PAKET database.

. paket.env

q='n'; read -n 1 -p "Clear all tables in ${PAKET_DB_NAME:-paket} database? [y|N] " q < /dev/tty; echo
if [ y = "$q" ]; then
    ./venv/bin/python ./init_db.py drop "../router"
fi

for server in "${PAKET_SERVERS[@]}"; do
    [ -f "../$server/db.py" ] && ./venv/bin/python ./init_db.py init "../$server"
done
