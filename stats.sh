#!/bin/bash
pushd "$(dirname "${BASH_SOURCE[0]}")"
. paket.env

if [ "$1" == servers ]; then
    if pgrep -fx 'python ./stats.py servers'; then
        echo 'servers stats already running'
        exit 1
    fi

    for subdomain in www route bridge fund explorer; do
        echo $subdomain $(curl -L --write-out %{http_code} --silent --output /dev/null https://$subdomain.paket.global)
    done | python ./stats.py servers

	events_count="$(curl -X POST --silent --header 'Content-Type: application/x-www-form-urlencoded' --header 'Accept: application/json' -d 'max_events_num=200' 'https://route.paket.global/v3/events' | python3 -c 'import sys, json; print(len(json.load(sys.stdin)["events"]))')"
    echo events_api $events_count | python ./stats.py servers

elif [ "$1" == commits ]; then
    if pgrep -fx 'python ./stats.py commits'; then
        echo 'commits stats already running'
        exit 1
    fi

    for repo in bridge explorer funder manager mobile paket-stellar router util webserver website; do
        repodir=/tmp/$repo
        [ -d $repodir ] || git clone --bare https://github.com/paket-core/$repo $repodir > /dev/null
        pushd $repodir > /dev/null
        git fetch > /dev/null
        git --no-pager log --all --numstat --format='%ct '$repo' %H %an' $(git reflog | awk '{print $1}')
        popd > /dev/null
    done | python ./stats.py commits

else
    $0 servers
    $0 commits
fi
popd
