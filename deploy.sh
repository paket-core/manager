#!/bin/bash
# Deploy PAKET servers.

. paket.env

# Get base source of repository.
DEFAULT_SOURCE=https://github.com/paket-core
SOURCE="$(grep -Pm1 'url\W*=\W*http' .git/config 2> /dev/null | grep -Po 'http.*(?=/manager)')"
SOURCE="${SOURCE:-$DEFAULT_SOURCE}"

activate_or_create_venv() {
    if ! [ -d venv ]; then
        python3 -m venv venv
        ./venv/bin/pip install --upgrade pip pycodestyle pylint
    fi
    . venv/bin/activate
}

clone_or_pull_repo() {
    echo "$1:"
    if [ -d "../$1" ]; then
        git -C "../$1" pull
    else
        git clone "$SOURCE/$1" "../$1"
    fi
    echo
}

# Get or update PAKET servers, collect requirements, and install them.
set -e
[ "$VIRTUAL_ENV" ] || activate_or_create_venv
for server in "${PAKET_SERVERS[@]}"; do
    clone_or_pull_repo $server
    requirements="$(cat "../$server/requirements.txt" <(echo "$requirements") | sort -u)"
done
while read package; do
    continue
    if [ "${package:0:3}" = '../' ]; then
        clone_or_pull_repo "${package:3}"
        requirements="$(cat "../$package/requirements.txt" <(echo "$requirements") | sort -u)"
    fi
done <<<"$requirements"
pip install -r <(echo "$requirements")
set +e

exit 0
