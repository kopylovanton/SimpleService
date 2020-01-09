# ************* Import
import logging
import os
import io
import yaml
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

cpage='utf-8'

# ************* Load Parms
with io.open(r'config/configdb.yaml', encoding = cpage) as file:
    parmsdb = yaml.load(file, Loader=yaml.FullLoader)

# ************* Load Parms
with io.open(r'config/config_get.yaml', encoding = cpage) as file:
    parms = yaml.load(file, Loader=yaml.FullLoader)

# ************* Logging
logFormat = '%(asctime)s =%(levelname)s= [%(name)s-%(lineno)d] - %(message)s'
#loghandler = TimedRotatingFileHandler("logfile",when="midnight")
logging.basicConfig(format=logFormat, level=logging.ERROR)

log = logging.getLogger(parms['URL'])
log.setLevel(parms['LOG_LEVEL'])
log.info('Start process worker')
# ************* check DB pass

salt = str.encode(os.uname()[4]+parmsdb['DB_CONN_STRING'])
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
    backend=default_backend())

if parmsdb['DB_USER_PASSWORD'].find('ENC_')!=0:
    parmsdb['SK'] = base64.urlsafe_b64encode(Fernet.generate_key()).decode(cpage)
    key = base64.urlsafe_b64encode(kdf.derive(parmsdb['SK'].encode(cpage)))
    kstore = Fernet(key)
    token = kstore.encrypt(parmsdb['DB_USER_PASSWORD'].encode(cpage))
    parmsdb['DB_USER_PASSWORD']='ENC_'+token.decode(cpage)
    with open('config/configdb.yaml', 'w') as outfile:
        yaml.dump(parmsdb, outfile, default_flow_style=False)
        log.info('DB password was encripted')
else:
    key = base64.urlsafe_b64encode(kdf.derive(parmsdb['SK'].encode(cpage)))
    kstore = Fernet(key)


from .wsstats import WSStatistic
from .db_connection_oracle import Oracle as db_connections

serviseStat = WSStatistic(parms['statDepts'])

ora = db_connections(parmsdb['DB_USER_NAME'], parmsdb['DB_USER_PASSWORD'][4:], \
                     parmsdb['DB_CONN_STRING'], parmsdb['DB_ENCODING'], log, parmsdb['CURRENT_SCHEMA'] )

__all__=['kstore','parms','parmsdb','log','db_connection_oracle','wsstats','service_get','serviseStat','ora']