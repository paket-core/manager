#!/bin/bash
# List git status of PAKET servers.

. paket.env

git_stat() {
    exec 6<&1
    exec 1>/dev/null
    pushd "$1"
    commit=$(git rev-parse HEAD)
    branch=$(git symbolic-ref HEAD | cut -d'/' -f3)
    if git status --porcelain | grep -v '^??'; then
        branch=dirty
    elif git log origin/$branch..HEAD | grep '^commit'; then
        branch=unpushed
    fi
    echo "$(pwd): $commit $branch" 1>&6
    popd
    exec 1<&6
}


for server in "${PAKET_SERVERS[@]}" manager; do
    git_stat "../$server"
    while read requirement; do
        if [ "${requirement:0:3}" = '../' ]; then
            git_stat "$requirement"
        fi
    done < "../$server/requirements.txt"
done | sort -u | column -t
