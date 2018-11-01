#!/bin/bash
# Run a funder routine.
pushd "$(dirname "${BASH_SOURCE[0]}")"
. ./paket.env
. ./venv/bin/activate
pushd ../funder
python ./routines.py "$1"
popd
popd
