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

# CHAIN = 'https://shenzhen.51nebula.com'
CHAIN = 'http://47.100.98.113:38090'

# sender = 'qi.sun@cybex.io'
sender = '313548025@qq.com'

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
################## ETO DATABASE ################
# ETO_MONGODB_DB_URL =  "mongodb://sunqi:sunqi123@127.0.0.1:27017/cybex"
ETO_MONGODB_DB_NAME='etoForm'

################## ETO DATABASE ################

# chain_id='ab1a36b889e21d2803219d379d10d39ff282b0399934946b1d5b799ceeb9fded'
chain_id='90be01e82b981c8f201c9a78a3d31f655743b29ff3274727b1439b093d04aa23'
# ws_conn = 'wss://shenzhen.51nebula.com/'
ws_conn = 'ws://47.100.98.113:38090'
# ws_conn = 'ws://uatfn.51nebula.com'
passwd = '12345678'
privk = '5KWTrrQMyD7Ez62viB36r75ur9ZJ6DPu3qkSa2eDcpE99XfD8ye'
faucet_account = 'sunxiaoqi-01'
