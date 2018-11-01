"""PaKeT database interface."""
import logging
import os

import util.db

LOGGER = logging.getLogger('pkt.db')
DB_HOST = os.environ.get('PAKET_DB_HOST', '127.0.0.1')
DB_PORT = int(os.environ.get('PAKET_DB_PORT', 3306))
DB_USER = os.environ.get('PAKET_DB_USER', 'root')
DB_PASSWORD = os.environ.get('PAKET_DB_PASSWORD')
DB_NAME = os.environ.get('PAKET_DB_NAME', 'paket')
SQL_CONNECTION = util.db.custom_sql_connection(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)


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
