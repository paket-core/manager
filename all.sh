#!/bin/bash
# Deploy/update, init database, test, and run PAKET servers.
./deploy.sh -y
./init_db.sh
./test.sh
./run.sh
