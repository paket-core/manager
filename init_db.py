"""Database initialization."""
import sys

import util.db
import util.logger
import webserver.validation


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(' usage: python ./init_db.py [drop|clear|init <package names>]')
        sys.exit()
    util.logger.setup()
    # This allows import from outside CWD.
    sys.path.append(sys.argv[2])
    # pylint: disable=import-error
    import db
    # pylint: enable=import-error
    if sys.argv[1] == 'drop':
        util.db.drop_tables(db.SQL_CONNECTION, db.DB_NAME)
    elif sys.argv[1] == 'clear':
        util.db.clear_tables(db.SQL_CONNECTION, db.DB_NAME)
    elif sys.argv[1] == 'init':
        db.init_db()
        webserver.validation.init_nonce_db()
