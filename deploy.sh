#!/bin/bash
# Deploy PAKET servers.

# Get base source of repository.
DEFAULT_SOURCE=https://github.com/paket-core
SOURCE="$(grep -Pm1 'url\W*=\W*git@' .git/config 2> /dev/null | grep -Po 'git@.*(?=/manager)')"
SOURCE="${SOURCE:-$(grep -Pm1 'url\W*=\W*http' .git/config 2> /dev/null | grep -Po 'http.*(?=/manager)')}"
SOURCE="${SOURCE:-$DEFAULT_SOURCE}"

# Get our single CLI flag.
if [ "$(printf "%s\n" "$1" | cut -c1)" = '-' ]; then
    UPDATE="$(printf "%s\n" "$1" | cut -c2)"
    shift
fi

update_repo() {
    echo "$1:"
    if [ -d "../$1" ]; then
        if [ "$UPDATE" ]; then
            q=$UPDATE
        else
            read -n 1 -p "Update local package at $1? [Y|n] " q < /dev/tty; echo
        fi
        [ "$q" = n ] || git -C "../$1" pull
    else
        git clone "$SOURCE/$1" "../$1"
    fi

    clean_package_name="$(tr '-' '_' <<<$1)"
    git_state_var_name="PAKET_GIT_STATE_${clean_package_name^^}"
    git_state="${!git_state_var_name:-master}"

    if [ "$UPDATE" ]; then
        q=$UPDATE
    else
        read -n 1 -p "Checkout $git_state? [Y|n] " q < /dev/tty; echo
    fi
    if ! [ "$q" = n ]; then
        git -C "../$1" pull
        git -C "../$1" checkout "$git_state"
        git -C "../$1" pull
    fi
}

# Get or update PAKET servers, collect requirements, and install them.
set -e
if ! [ -d venv ]; then
    python3 -m venv venv
fi
. paket.env
pip install --upgrade pip pycodestyle pylint

for server in "${PAKET_SERVERS[@]}"; do
    update_repo $server
    requirements="$(cat "../$server/requirements.txt" <(echo "$requirements") | sort -u)"
done
while read package; do
    if [ "${package:0:3}" = '../' ]; then
        update_repo "${package:3}"
        requirements="$(cat "$package/requirements.txt" 2> /dev/null <(echo "$requirements") | sort -u)"
    fi
done <<<"$requirements"
pip install -r <(echo "$requirements")
set +e
