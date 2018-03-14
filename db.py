'PaKeT database interface.'
import contextlib
import logging
import sqlite3

LOGGER = logging.getLogger("pkt.{}".format(__name__))
DB_NAME = 'paket.db'


class UnknownUser(Exception):
    'Invalid user ID.'


@contextlib.contextmanager
def sql_connection(db_name=DB_NAME):
    'Context manager for querying the database.'
    try:
        connection = sqlite3.connect(db_name)
        yield connection.cursor()
        connection.commit()
    except sqlite3.Error as db_exception:
        raise db_exception
    finally:
        if 'connection' in locals():
            connection.close()


def init_db():
    'Initialize the database.'
    with sql_connection() as sql:
        # Not using IF EXISTS here in case we want different handling.
        sql.execute('SELECT name FROM sqlite_master WHERE type = "table" AND name = "users"')
        if len(sql.fetchall()) == 1:
            LOGGER.debug('table already exists')
            return
        sql.execute('''
            CREATE TABLE users(
                address VARCHAR(42) PRIMARY KEY,
                user_id VARCHAR(32) UNIQUE,
                kwargs VARCHAR(1024))''')
        LOGGER.debug('table created')
        sql.execute('CREATE UNIQUE INDEX address_index ON users(address);')
        sql.execute('CREATE UNIQUE INDEX user_id_index ON users(user_id);')
        LOGGER.debug('indices created')


def set_users(users):
    'Set some users for testing.'
    with sql_connection() as sql:
        for user_id, address in users.items():
            try:
                sql.execute("INSERT INTO users (user_id, address) VALUES (?, ?)", (user_id, ''))
            except sqlite3.IntegrityError:
                pass
            sql.execute("UPDATE users SET address = ? WHERE user_id = ?", (address, user_id))
            users = sql.fetchone()


def get_users():
    'Get list of users and addresses - for debug only.'
    with sql_connection() as sql:
        sql.execute('SELECT user_id, address FROM users')
        return sql.fetchall()


def get_user_address(user_id):
    'Get the address of a user. Raise exception if the user is unknown.'
    with sql_connection() as sql:
        sql.execute('SELECT address FROM users WHERE user_id = ?', (user_id,))
        try:
            return sql.fetchone()[0]
        except TypeError:
            raise UnknownUser("Unknown user {}".format(user_id))
