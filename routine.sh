#!/bin/bash
# Run a funder routine.
. ./paket.env
. ./venv/bin/activate
pushd ../funder
python ./routines.py "$1"
popd
