#!/bin/bash
# Deploy PAKET servers.

. paket.env

# Get base source of repository.
DEFAULT_SOURCE=https://github.com/paket-core
SOURCE="$(grep -Pm1 'url\W*=\W*git@' .git/config 2> /dev/null | grep -Po 'git@.*(?=/manager)')"
SOURCE="${SOURCE:-$(grep -Pm1 'url\W*=\W*http' .git/config 2> /dev/null | grep -Po 'http.*(?=/manager)')}"
SOURCE="${SOURCE:-$DEFAULT_SOURCE}"

activate_or_create_venv() {
    if ! [ -d venv ]; then
        python3 -m venv venv
        ./venv/bin/pip install --upgrade pip pycodestyle pylint
    fi
    . venv/bin/activate
}

clone_or_fetch_repo() {
    echo "$1:"
    if [ -d "../$1" ]; then
        read -n 1 -p "Update local package at $1? [Y|n] " q < /dev/tty; echo
        [ "$q" = n ] && return 0
        git -C "../$1" fetch
    else
        git clone "$SOURCE/$1" "../$1"
    fi
    clean_package_name="$(tr '-' '_' <<<$1)"
    git_state_var_name="PAKET_GIT_STATE_${clean_package_name^^}"
    git_state="${!git_state_var_name}"
    if [ "$git_state" ]; then
        read -n 1 -p "Checkout $git_state? [Y|n] " q < /dev/tty; echo
        [ "$q" = n ] || git -C "../$1" checkout "$git_state"
    fi
    echo
}

# Get or update PAKET servers, collect requirements, and install them.
set -e
[ "$VIRTUAL_ENV" ] || activate_or_create_venv
for server in "${PAKET_SERVERS[@]}"; do
    clone_or_fetch_repo $server
    requirements="$(cat "../$server/requirements.txt" <(echo "$requirements") | sort -u)"
done
while read package; do
    if [ "${package:0:3}" = '../' ]; then
        clone_or_fetch_repo "${package:3}"
        requirements="$(cat "$package/requirements.txt" 2> /dev/null <(echo "$requirements") | sort -u)"
    fi
done <<<"$requirements"
pip install -r <(echo "$requirements")
set +e
