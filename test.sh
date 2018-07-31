#!/bin/bash
# Test PAKET packages.

. paket.env

for server in "${PAKET_SERVERS[@]}"; do
    requirements="$(cat "../$server/requirements.txt" <(echo -e "$requirements\n../$server") | sort -u)"
done
PAKET_DB_NAME=test
export PAKET_DB_NAME
while read package; do
    if [ "${package:0:3}" = '../' ]; then
        pushd "$package" > /dev/null
        echo
        pwd
        echo ---
        which pycodestyle > /dev/null && \
            echo pycodestyle had $(pycodestyle --max-line-length=120 **/*.py 2>&1 | wc -l) issues
        which pylint > /dev/null && \
            pylint **/*.py 2>&1 | tail -2 | head -1
        python -m unittest 2>&1 | tail -3 | head -1
        popd > /dev/null
    fi
done <<<"$requirements"
