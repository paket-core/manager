#!/bin/bash
# Initialize PAKET database.

. paket.env

q='n'; read -n 1 -p "Clear all tables in ${PAKET_DB_NAME:-paket} database? [y|N] " q < /dev/tty; echo
if [ y = "$q" ]; then
    PYTHONPATH="$PYTHONPATH" ./venv/bin/python -c '
from util.db import drop_tables
import sys
sys.path.append("../api")
import db
drop_tables(db.SQL_CONNECTION, db.DB_NAME)
    '
fi

for server in "${PAKET_SERVERS[@]}"; do
    pushd "../$server"
    python -c "import util.logger as l; l.setup(); import db; db.init_db()"
    popd
done
python -c "import util.logger as l; l.setup(); from webserver import validation as v; v.init_nonce_db()"

exit 0
