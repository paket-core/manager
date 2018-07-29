#!/bin/bash
# Deploy a PaKeT server.

. paket.env

SERVERS=(api funder)
for server in "${SERVERS[@]}"; do
    pushd "../$server"
    python -c "import util.logger as l; l.setup(); import db; db.init_db()"
    popd
done
python -c "import util.logger as l; l.setup(); from webserver import validation as v; v.init_nonce_db()"

exit 0
