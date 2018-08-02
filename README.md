PAKET Manager
=============

The PAKET Manager is a small collection of scripts used to autoatically deploy, test, and run PAKET software.

Setup Your Manager
------------------

1. Create a project directory and enter it:
```shell
mkdir paket
cd paket
```

2. Clone the repository inside the project directory:
```shell
git clone git@github.com:paket-core/manager
```

Note that this method requires using SSH keys. If you would rather clone the
repository over public access simply use:
```shell
git clone https://github.com/paket-core/manager
```

3. Create a python virtual environment:
```shell
python3 -m venv venv
```

4. Activate the python virtual environment:
```shell
. venv/bin/activate
```

5. Make sure you are using an updated pip:
```shell
pip install --upgrade pip
```

6. Make sure your `paket.env` contains all desired variables and values.

System settings:
  * `PAKET_SERVERS` - an array of servers you wish to run - recommended value (with parenthesis): (funder api)

Stellar settings:
  * `PAKET_ISSUER_PUBKEY` - the issuer pubkey (has no default, software will
    refuse to run without it)
  * `PAKET_HORIZON_SERVER` - your preferred horizon server (defaults to
    'https://horizon-testnet.stellar.org')

Payment settings:
  * `PAKET_FUNDER_SEED` - the seed for an account that sells BUL and XLM
  * `PAKET_PAYMENT_XPUB` - an x-public-key for generating payment addresses
  * `PAKET_BUL_STROOPS_FOR_EUR_CENT` - the integer number of BUL stroops that a EUR cent buys
  * `PAKET_BASIC_MONTHLY_ALLOWANCE` - monthly purchase allowance for a user that passed basic KYC check
  * `PAKET_MINUMUM_PAYMENT` - minimal acceptable payment in EUR cents
  * `PAKET_ETHERSCAN_API_KEY` - an API key for monitoring ETH payments

Database (MySQL) access settings:
  * `PAKET_DB_HOST` - the host of your MySQL server (defaults to '127.0.0.1')
  * `PAKET_DB_PORT` - the port of your MySQL server (defaults to 3306)
  * `PAKET_DB_USER` - the user on your MySQL server (defaults to 'root')
  * `PAKET_DB_PASSWORD` - the user on your MySQL server (defaults to None)

Webserver settings:
  * `PAKET_SESSIONS_KEY` - a secret session key, for securing user sessions
    (defaults to `os.urandom(24)` in runtime)
  * `PAKET_SERVER_LIMIT` - the default rate limit of your servers (defaults to
    '100 per minute')
  * `PAKET_API_PORT` - the port on which the funding server will run (defaults
    to 8000)
  * `PAKET_FUNDER_PORT` - the port on which the funding server will run
    (defaults to 8001)

Logging settings:
  * `PAKET_LOG_DIR` - the path on the filesystem to store the log file in
    (defaults to './')
  * `PAKET_LOG_FILE` - the name of the log file (defaults to 'paket.log')
  * `PAKET_LOG_FMT` - log format, using python logging standartds (defaults to
    '%(asctime)s %(levelname).3s: %(message)s - %(name)s +%(lineno)03d')
  * `PAKET_LOG_DATE_FMT' - log date format, using python logging standartds
    (defaults to '%Y-%m-%d %H:%M:%S')
  * `PAKET_LOG_LEVEL` - the minimal logging level, using python standartds
    (defaults to 10, which is `logging.DEBUG`)

Debugging settings (DO NOT USE THEM ON PRODUCTION ENVIRONMENT):
  * `PAKET_ISSUER_SEED` - the issuer seed (defaults to None)
  * `PAKET_DEBUG` - to run PAKET software in debug mode, with debug calls and no signature checking.
  * `FLASK_DEBUG` - to run the web server in debug mode with auto reloading.

Deploy, Test, and Run PAKET Software
------------------------------------

1. Deploy the software:
```shell
./deploy.sh
```

Note that this will create several directories in the project directory, which is the repository's *parent* directory.

2. Initialize the database:
```shell
./init_db.sh
```

3. Test the software:
```shell
./test.sh
```

If you wish to use pycodestyle and/or pylint in your tests, just install them
into your virtual environment and the script will take care of the rest:
```shell
pip install pycodestyle pylint
```

4. Run the servers:
```shell
./run.sh
```

5. Access the swagger Web interfaces from a browser (that the ports will change
   according to your webserver settings):
  * http://localhost:8000
  * http://localhost:8001
