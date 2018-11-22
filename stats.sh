#!/bin/bash
if ! [ "$1" ]; then
    echo "Usage: $0 [servers|commits|logs]"
    exit 2
fi

LOCKDIR="/tmp/stats.$1.lock"
if ! mkdir $LOCKDIR; then
    echo stats "$1" is already running, aborting
    exit 1
fi

pushd "$(dirname "${BASH_SOURCE[0]}")"
. paket.env

if [ "$1" == servers ]; then
    for subdomain in www route bridge fund explorer; do
        echo $subdomain $(curl -L --write-out %{http_code} --silent --output /dev/null https://$subdomain.paket.global)
    done | python ./stats.py servers

    echo router_api $(curl -L --write-out %{http_code} --silent --output /dev/null -X POST http://route.paket.global/v3/events) | python ./stats.py servers

    echo stellar-testnet $(curl -L --write-out %{http_code} --silent --output /dev/null https://horizon-testnet.stellar.org/) | python ./stats.py servers

elif [ "$1" == commits ]; then
    for repo in bridge explorer funder manager mobile paket-stellar router util webserver website; do
        repodir=/tmp/$repo
        [ -d $repodir ] || git clone --bare https://github.com/paket-core/$repo $repodir > /dev/null
        pushd $repodir > /dev/null
        git fetch > /dev/null
        last_commit_timestamp="$(echo "SELECT UNIX_TIMESTAMP(timestamp) FROM commits WHERE repo = '$repo' ORDER BY timestamp DESC LIMIT 1" | mysql -sNh"$PAKET_DB_HOST" -u"$PAKET_DB_USER" -p"$PAKET_DB_PASSWORD" "$PAKET_DB_NAME")"
        [ "$last_commit_timestamp" ] && since="--since=$last_commit_timestamp"
        git --no-pager log --all $since --numstat --format='%ct '$repo' %H %an'
        popd > /dev/null
    done | python ./stats.py commits

elif [ "$1" == logs ]; then
    LOGFILE=/var/log/paket.log
    tac $LOGFILE | head -1000 | grep ' ERR: ' | python ./stats.py logs

fi
popd
rmdir $LOCKDIR
