import os

# qconn = q.q(host = 'localhost', port = 8083, user = 'sunqi')
# Q_HOST = os.environ.get('Q_HOST_ADDR','localhost')
Q_HOST = os.environ.get('Q_HOST_ADDR','localhost')
Q_PORT = os.environ.get('Q_PORT', 9093)
Q_USER= os.environ.get('Q_USER', 'sunqi:sunqi123')

FAUCET_URL = 'http://localhost:8087'
FAUCET_register = FAUCET_URL + '/register/' 
FAUCET_status = FAUCET_URL + '/register/status/'

MONGODB_DB_URL = os.environ.get('MONGO_WRAPPER', "mongodb://faucet:faucet123@127.0.0.1:27017/cybex_faucet_test") # clockwork
#MONGODB_DB_NAME_FAUCET = os.environ.get('MONGO_DB_NAME', 'faucet')
MONGODB_DB_NAME_KYC = os.environ.get('MONGO_DB_NAME', 'cybex_faucet_test')

CHAIN = 'https://shenzhen.51nebula.com'

sender = 'qi.sun@cybex.io'

# Database connection: see https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-PARAMKEYWORDS
# Cache: see https://flask-caching.readthedocs.io/en/latest/#configuring-flask-caching
CACHE = {
    'CACHE_TYPE': os.environ.get('CACHE_TYPE', 'simple'),
    'CACHE_DEFAULT_TIMEOUT': int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 600)) # 10 min
}

# Configure profiler: see https://github.com/muatik/flask-profiler
PROFILER = {
    'enabled': os.environ.get('PROFILER_ENABLED', False),
    'username': os.environ.get('PROFILER_USERNAME', None),
    'password': os.environ.get('PROFILER_PASSWORD', None),
}

