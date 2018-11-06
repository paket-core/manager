#!/usr/bin/env python
"Collect stats and toss them in a table"
import datetime
import logging
import os

import requests

import util.logger
import util.db

LOGGER = logging.getLogger('pkt.db')
DB_HOST = os.environ.get('PAKET_DB_HOST', '127.0.0.1')
DB_PORT = int(os.environ.get('PAKET_DB_PORT', 3306))
DB_USER = os.environ.get('PAKET_DB_USER', 'root')
DB_PASSWORD = os.environ.get('PAKET_DB_PASSWORD')
DB_NAME = os.environ.get('PAKET_DB_NAME', 'paket')
SQL_CONNECTION = util.db.custom_sql_connection(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

util.logger.setup()


def init_db():
    """Initialize the database."""
    with SQL_CONNECTION() as sql:
        sql.execute('''
            CREATE TABLE stats(
                timestamp TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                metric VARCHAR(256) NOT NULL,
                value VARCHAR(256) NOT NULL)''')
        LOGGER.debug('stats table created')


def add_stat(metric, value, timestamp=None):
    """Add a stat."""
    with SQL_CONNECTION() as sql:
        sql.execute("INSERT INTO stats VALUES(%s, %s, %s)", (timestamp, metric, value))


def clear_stat(metric):
    """Remove all stats of a specific metric."""
    with SQL_CONNECTION() as sql:
        sql.execute("DELETE FROM stats WHERE metric = %s", (metric,))


def get_stat(metric=None, from_time=None, limit=None):
    """Get all stats, optionally of a specified metric, optionally from a specified time."""
    conditions, args = ['1'], []
    if metric:
        conditions.append('AND metric like %s')
        args.append(metric)
    if from_time:
        conditions.append('AND timestamp >= %s')
        args.append(from_time)
    conditions.append('ORDER BY timestamp DESC')
    if limit:
        conditions.append('LIMIT %s')
        args.append(limit)
    with SQL_CONNECTION() as sql:
        print("SELECT * FROM stats {}".format(' '.join(conditions)))
        sql.execute("SELECT * FROM stats WHERE {}".format(' '.join(conditions)), args)
        return sql.fetchall()


# Server stats
SERVERS = ['route', 'bridge', 'fund', 'explorer']


def get_server_stat(server_uri):
    """Check server status."""
    try:
        return requests.get(server_uri).status_code == 200
    # pylint: disable=broad-except
    except Exception:
        return False


# GitHub stats
REPOS = [
    'bridge', 'funder', 'manager', 'mobile', 'os-projects', 'paket-stellar',
    'router', 'util', 'webserver', 'website']


def get_commits_from_page(repo, page=1, get_num_of_pages=False):
    """Get data from a commits page."""
    page = requests.get("https://api.github.com/repos/paket-core/{}/commits?page={}".format(repo, page))
    commits = [{
        'hash': commit['sha'],
        'author': commit['commit']['author']['name'],
        'timestamp': datetime.datetime.strptime(commit['commit']['author']['date'], '%Y-%m-%dT%H:%M:%SZ')
    } for commit in page.json()]

    if get_num_of_pages:
        num_of_pages = int([
            link['url'].split('page=')[1]
            for link in requests.utils.parse_header_links(page.headers['link'])
            if link['rel'] == 'last'][0])
        return commits, num_of_pages
    return commits


def get_repo_commits(repo, from_time=None):
    """Get all commits of a repo from a point in time."""
    if not from_time:
        from_time = datetime.datetime.now() - datetime.timedelta(days=30)
    commits, num_of_pages = get_commits_from_page(repo, get_num_of_pages=True)
    if commits[-1]['timestamp'] >= from_time:
        for page_number in range(2, num_of_pages + 1):
            if commits[-1]['timestamp'] < from_time:
                break
            commits += get_commits_from_page(repo, page_number)

    for commit_index in range(len(commits) - 1, -1, -1):
        if commits[commit_index]['timestamp'] >= from_time:
            break
        commits.pop()
    return commits


def insert_new_commits(repo):
    """Get commits from all repos from a specified time."""
    try:
        last_commit_timestamp = get_stat("commit_{}_*".format(repo), limit=1)[0]['timestamp']
    except IndexError:
        last_commit_timestamp = datetime.datetime.fromtimestamp(0)
    for commit in get_repo_commits(repo, last_commit_timestamp):
        add_stat("commit_{}_{}".format(repo, commit['author']), 1, commit['timestamp'])


if __name__ == '__main__':
    for server_name in SERVERS:
        add_stat(server_name, 1 if get_server_stat(
            "https://{}.paket.global".format(server_name)
        ) else 0)
    _ = [insert_new_commits(repo) for repo in REPOS]
