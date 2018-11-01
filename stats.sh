#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
pushd "$(dirname "$0")"
. paket.env
./venv/bin/python ./stats.py
popd
