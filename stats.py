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


def add_server_status(subdomain, status):
    """Add a stat."""
    with SQL_CONNECTION() as sql:
        sql.execute("INSERT INTO servers(subdomain, trouble) VALUES(%s, %s)", (
            subdomain, 0 if int(status) == 200 else 1))


def add_commit(args):
    """Add a commit."""
    with SQL_CONNECTION() as sql:
        sql.execute("INSERT INTO commits VALUES(%s, %s, %s, %s, %s, %s, %s)", args)


def convert_timestamp(unix_string):
    """Convert a string holding an integer unix timestamp to a datetime object."""
    return datetime.datetime.fromtimestamp(int(unix_string))


def insert_servers():
    """Insert server stats."""
    for line in sys.stdin:
        add_server_status(*line.split(' '))


def insert_commits():
    """Insert commit details."""
    commit = {}
    for line in sys.stdin.readlines() + ['0']:
        if line == '\n':
            continue
        fields = line.strip().split(' ')
        try:
            timestamp = convert_timestamp(fields[0])
            if commit:
                try:
                    add_commit([commit[key] for key in [
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


# FIXME This is just for the Belgrade demo.
def launch_demo_packages():
    """Launch demo packages if there aren't enough already"""
    oren_pubkey = 'orenpk'
    yamit_pubkey = 'yamitpk'
    oren_contact = 'orencnt'
    yamit_contact = 'yamircnt'
    from_location = 'from_location'
    to_location = 'to location'
    from_address = 'from address'
    to_address = 'to address'
    with SQL_CONNECTION() as sql:
        sql.execute("""
            select count(1) as count from packages
            where launcher_pubkey = %s
            and escrow_pubkey not in (
                select escrow_pubkey from events where event_type = 'courier confirmed')""", (oren_pubkey,))
        if int(sql.fetchone()[b'count']) >= 2:
            return

        import time
        import paket_stellar
        escrow_keypair = paket_stellar.stellar_base.Keypair.random()
        escrow_pubkey = escrow_keypair.address().decode()
        escrow_seed = escrow_keypair.seed().decode()
        sql.execute("""
            insert into packages (
                escrow_pubkey, launcher_pubkey, recipient_pubkey, launcher_contact, recipient_contact, payment,
                collateral, deadline, description, from_location, to_location, from_address, to_address
            ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            escrow_pubkey, oren_pubkey, yamit_pubkey, oren_contact, yamit_contact,
            50 * 10**7, 1 * 10**7, int(time.time()) + 60 * 60 * 24 * 2, 'Your business card',
            from_location, to_location, from_address, to_address))
        sql.execute("""
            insert into events (user_pubkey, event_type, location, escrow_pubkey, kwargs)
            values (%s, %s, %s, %s, %s)
        """, (oren_pubkey, 'launched', from_location, escrow_pubkey, '{}'))
        sql.execute("""
            insert into events (user_pubkey, event_type, location, escrow_pubkey, kwargs)
            values (%s, %s, %s, %s, %s)
        """, (
            oren_pubkey, 'escrow seed added', from_location, escrow_pubkey,
            "{{'escrow_seed': '{}'}}".format(escrow_seed)))

if __name__ == '__main__':
    launch_demo_packages()
    sys.exit(4)
    if len(sys.argv) != 2:
        sys.exit(1)
    if sys.argv[1] == 'servers':
        insert_servers()
    elif sys.argv[1] == 'commits':
        insert_commits()
