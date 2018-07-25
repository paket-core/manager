#!/bin/bash
# Deploy PAKET servers.

! [ "$VIRTUAL_ENV" ] && echo "refusing to install outside of virtual env" && exit 1

# Get base source of repository.
default_source=https://github.com/paket-core/manager
source="$(grep -Pm1 'url\W*=\W*http' .git/config 2> /dev/null | grep -Po 'http.*(?=/manager)')"
source="${source:-$default_source}"

clone_or_pull() {
    repo="$1"
    if [ -d "../$repo" ]; then
        git -C "../$repo" pull
    else
        git clone "$source/$repo" "../$repo"
    fi
}

# Get or update PAKET servers, collect requirements, and install them.
SERVERS=(api funder)
set -e
for server in "${SERVERS[@]}"; do
    clone_or_pull $server
    requirements="$(cat ../$server/requirements.txt <(echo $requirements) | sort -u)"
done
while read package; do
    if [ "${package:0:3}" = '../' ]; then
        clone_or_pull "${package:3}"
    fi
    pip install "$package"
done <<<$requirements
set +e

exit 0
