#!/usr/bin/env python
"Collect stats and toss them in a table"
import datetime
import logging
import sys
import os

import util.db
import util.logger

LOGGER = logging.getLogger('pkt.stats')
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
            CREATE TABLE servers(
                timestamp TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                subdomain VARCHAR(256) NOT NULL,
                trouble INTEGER NOT NULL)''')
        LOGGER.debug('servers table created')
        sql.execute('''
            CREATE TABLE commits(
                timestamp TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                repo VARCHAR(32) NOT NULL,
                hash VARCHAR(40) NOT NULL UNIQUE,
                author VARCHAR(256) NOT NULL,
                files_changed INTEGER,
                insertions INTEGER,
                deletions INTEGER)''')
        LOGGER.debug('commits table created')
        sql.execute('''
            CREATE TABLE log_errors(
                timestamp TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
                message VARCHAR(256) NOT NULL,
                location VARCHAR(32) NOT NULL)''')
        LOGGER.debug('log errors table created')


def convert_timestamp(unix_string):
    """Convert a string holding an integer unix timestamp to a datetime object."""
    return datetime.datetime.fromtimestamp(int(unix_string))


def insert_servers():
    """Insert server stats."""
    with SQL_CONNECTION() as sql:
        for line in sys.stdin:
            subdomain, status = line.split(' ')
            sql.execute("INSERT INTO servers(subdomain, trouble) VALUES(%s, %s)", (
                subdomain, 0 if int(status) == 200 else 1))


def insert_commits():
    """Insert commit details."""
    commit = {}
    with SQL_CONNECTION() as sql:
        for line in sys.stdin.readlines() + ['0']:
            if line == '\n':
                continue
            fields = line.strip().split(' ')
            try:
                timestamp = convert_timestamp(fields[0])
                if commit:
                    try:
                        sql.execute("INSERT INTO commits VALUES(%s, %s, %s, %s, %s, %s, %s)", [commit[key] for key in [
                            'timestamp', 'repo', 'hash', 'author', 'files_changed', 'insertions', 'deletions']])
                    except util.db.mysql.connector.errors.IntegrityError:
                        LOGGER.warning("duplicate commit: %s", commit)
                if line == '0':
                    break
                commit = {
                    'timestamp': timestamp,
                    'repo': fields[1],
                    'hash': fields[2],
                    'author': '-'.join(fields[3:]),
                    'files_changed': 0,
                    'insertions': 0,
                    'deletions': 0}
            except ValueError:
                fields = fields[0].split('\t')
                commit['files_changed'] += 1
                if fields[0].isdigit():
                    commit['insertions'] += int(fields[0])
                if fields[1].isdigit():
                    commit['deletions'] += int(fields[1])


def insert_log_errors():
    """Insert log errors."""
    with SQL_CONNECTION() as sql:
        for line in sys.stdin:
            words = line.split(' ')
            timestamp, message, location = [' '.join(field).strip() for field in [words[:2], words[2:-3], words[-2:]]]
            LOGGER.warning("%s|%s|%s", timestamp, message, location)
            sql.execute("INSERT INTO log_errors VALUES(%s, %s, %s)", (timestamp, message, location))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(1)
    if sys.argv[1] == 'servers':
        insert_servers()
    elif sys.argv[1] == 'commits':
        insert_commits()
    elif sys.argv[1] == 'logs':
        insert_log_errors()
