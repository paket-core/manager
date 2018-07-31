"""Database initialization."""
import sys

import util.db
import util.logger
import webserver.validation


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(' usage: python ./init_db.py [drop|clear|init <package names>]')
        sys.exit()
    util.logger.setup()
    if sys.argv[1] == 'drop':
        # This allows import from outside CWD.
        sys.path.append('../api')
        # pylint: disable=import-error
        import db
        # pylint: enable=import-error
        util.db.drop_tables(db.SQL_CONNECTION, db.DB_NAME)
    elif sys.argv[1] == 'init':
        # This allows import from outside CWD.
        sys.path.append(sys.argv[2])
        # pylint: disable=import-error
        import db
        # pylint: enable=import-error
        db.init_db()
        webserver.validation.init_nonce_db()
