# ************* Import
import base64
import io
import os
import sys
import time
from concurrent import futures
from typing import Dict

import cx_Oracle
import yaml
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .logconf import LoguruLogger


# ************* Oracle connection
class Oracle(LoguruLogger):

    def __init__(self, lpatch, enccp: str = 'utf-8'):
        self.db_connected = False
        super().__init__(lpatch)
        self.cpage = enccp
        self.db_connected = False
        self.parmsdb = self._load_db_parms(lpatch)
        with self.log.catch(message='Error load DB connections configurations:', onerror=lambda _: sys.exit(1)):
            for p in ['DB_CONN_STRING', 'DB_USER_NAME', 'DB_USER_PASSWORD', 'DB_ENCODING', 'CURRENT_SCHEMA',
                      'DB_EXECUTE_TIMEOUT', 'DB_CONN_POOL']:
                if len(str(self.parmsdb[p])) < 1:
                    self.log.critical('/config/config_db.yaml -> %s does not defined' % p)
                    raise ValueError
        self.kstore = self._kstore()
        self.username = self.parmsdb['DB_USER_NAME']
        self.pwd = self.parmsdb['DB_USER_PASSWORD'][4:]
        self.conn_string = self.parmsdb['DB_CONN_STRING']
        self.encoding = self.parmsdb['DB_ENCODING']
        self.current_schema = self.parmsdb['CURRENT_SCHEMA']
        self.callTimeout = self.parmsdb['DB_EXECUTE_TIMEOUT']
        self.connPolSize = int(self.parmsdb['DB_CONN_POOL'])
        self.StatSQLDurationMean = 0
        self.StatPLSQLDurationMean = 0
        self.connPol = None
        self.dbExecutor = None
        try:
            self.db_connect('-=StartUP=-')
        except cx_Oracle.DatabaseError as e:
            self.db_connected = False
            error_obj, = e.args
            self.log.error('DB <%s> have not connected.  Oracle error message: ' % self.conn_string + str(
                error_obj.message))

    def __del__(self):
        self.db_disconnect()

    def get_password(self):
        try:
            pwd = self.kstore.decrypt(self.pwd.encode(self.cpage)).decode(self.cpage)
        except InvalidToken:
            self.log.error('Get error during restore encrypted DB password. ' +
                           'Please change password in config_db.yaml to unecripted and restart service')
            raise InvalidToken
        return pwd

    def set_thread_pool_executor(self, force: bool = False):
        if self.dbExecutor is None:
            self.dbExecutor = futures.ThreadPoolExecutor(max_workers=self.connPolSize)
        if force:
            self.dbExecutor = futures.ThreadPoolExecutor(max_workers=self.connPolSize)
        # if self.dbExecutor._shutdown:
        #     self.dbExecutor = futures.ThreadPoolExecutor(max_workers=self.connPolSize)

    def db_connect(self, uid: str = 'internal'):
        """ Connect to the database. """
        if self.db_connected:
            return
        try:
            self.connPol = cx_Oracle.SessionPool(self.username, self.get_password(), self.conn_string,
                                                 min=self.connPolSize, max=self.connPolSize,
                                                 encoding=self.encoding, threaded=True)
            if self.db_is_connect():
                self.db_connected = True
                self.log.info('Message IDT:%s - DB <%s> connection started' % (uid, self.conn_string))
            self.set_thread_pool_executor()
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db_connected = False
            self.log.error(
                'Message IDT:%s - Can not connect to DB <%s>. Oracle error message: ' % (uid, self.conn_string) + str(
                    error_obj.message))
            self.dbExecutor = None

    def db_disconnect(self):
        """
        Disconnect from the database. If this fails, for instance
        if the connection instance doesn't exist, ignore the exception.
        """
        if not self.db_connected:
            return
        self.db_connected = False
        try:
            self.dbExecutor.shutdown(wait=True)
            self.connPol.close()
            self.log.warning('DB <%s> connection finished' % self.conn_string)
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.log.warning('DB <%s> connection finished with some eception' % str(error_obj.message))
        self.dbExecutor = None

    def sync_sql(self, sql: str, bind_vars=None, uid: str = 'unknown', fetchcount: int = 1000) -> Dict:
        """
        Execute whatever SQL statements are passed to the method;
        commit if specified. Do not specify fetchall() in here as
        the SQL statement may not be a select.
        bindvars is a dictionary of variables you pass to execute.
        """
        if bind_vars is None:
            bind_vars = {}
        start_time = time.time()
        resp = {'rc': 200,
                'message': 'Success',
                'records': []
                }
        if not self.db_connected:
            self.db_connect(uid=uid)
        if not self.db_connected:
            resp = {'rc': 500,
                    'message': 'DB <%s> connection DOWN' % self.conn_string,
                    'records': [],
                    'sqld': '-'
                    }
        if self.db_connected:
            try:
                with self.connPol.acquire() as conn:
                    conn.current_schema = self.current_schema
                    conn.callTimeout = self.callTimeout
                    with conn.cursor() as cursor:
                        cursor.execute(sql, bind_vars)
                        rows = cursor.fetchmany(fetchcount)
                        columns = [i[0] for i in cursor.description]
                        resp['records'] = [dict(zip(columns, row)) for row in rows]
                    sqld = round(time.time() - start_time, 4)
                    self.StatSQLDurationMean = round((1.8 * self.StatSQLDurationMean + 0.2 * sqld) / 2, 4)
                    resp['sqld'] = str(sqld)
            except cx_Oracle.DatabaseError as e:
                error_obj, = e.args
                resp = {'rc': 500,
                        'message': 'Can not execute SQL. Oracle error message: ' + str(error_obj.message),
                        'records': [],
                        'sqld': '-'
                        }
                self.log.error(
                    'Message IDT:%s - Can not execute SQL . Oracle error message: ' % uid + str(error_obj.message))
                self.db_disconnect()
        return resp

    def sync_plsql(self, plsql: str = "begin :len := length(:inP); end;", in_val=None,
                   out_val=None, uid: str = 'unknown') -> Dict:
        if out_val is None:
            out_val = ['len']
        if in_val is None:
            in_val = {'inP': 'Hello World'}
        start_time = time.time()
        resp = {'rc': 200,
                'message': 'Success'
                }
        if not self.db_connected:
            self.db_connect(uid=uid)
        if not self.db_connected:
            resp = {'rc': 500,
                    'message': 'DB <%s> connection DOWN' % self.conn_string,
                    'sqld': '-'
                    }
        if self.db_connected:
            try:
                with self.connPol.acquire() as conn:
                    conn.current_schema = self.current_schema
                    conn.callTimeout = self.callTimeout
                    with conn.cursor() as cursor:
                        io_parms: Dict[str, str] = in_val.copy()
                        for f in out_val:
                            io_parms[f] = cursor.var(str)
                        cursor.execute(plsql, **io_parms)
                        for f in out_val:
                            resp[f] = io_parms[f].getvalue()
                    sqld = round(time.time() - start_time, 4)
                    self.StatPLSQLDurationMean = round((1.8 * self.StatPLSQLDurationMean + 0.2 * sqld) / 2, 4)
                    resp['sqld'] = str(sqld)
            except cx_Oracle.DatabaseError as e:
                error_obj, = e.args
                resp = {'rc': 500,
                        'message': 'Can not execute PL/SQL. Oracle error message: ' + str(error_obj.message),
                        'sqld': '-'
                        }
                self.log.error(
                    "Message IDT:%s - Can not execute PL/SQL . Oracle error message: " % uid + str(error_obj.message))
                self.db_disconnect()

        return resp

    def _db_not_connect(self):
        """ Check DB status """
        try:
            with self.connPol.acquire() as conn:
                conn.current_schema = self.current_schema
                conn.callTimeout = self.callTimeout
                cursor = conn.cursor()
                cursor.execute('select 1 from dual')
                cursor.close()
            self.db_connected = True
            # self.log.info('Status DB <%s> connection UP' % (self.conn_string))
            return False
        except cx_Oracle.DatabaseError as e:
            error_obj, = e.args
            self.db_connected = False
            self.log.warning('Status DB <%s> connection DOWN; ' % self.conn_string +
                             'Oracle error message: ' + str(error_obj.message))
            self.db_disconnect()
            return True

    def db_is_connect(self):
        """ Check DB status """
        return not self._db_not_connect()
        # ************* check DB pass

    def _kstore(self):
        salt = str.encode(os.uname()[4] + self.parmsdb['DB_CONN_STRING'])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend())

        if self.parmsdb['DB_USER_PASSWORD'].find('ENC_') != 0:
            self.parmsdb['SK'] = base64.urlsafe_b64encode(Fernet.generate_key()).decode(self.cpage)
            key = base64.urlsafe_b64encode(kdf.derive(self.parmsdb['SK'].encode(self.cpage)))
            kstore = Fernet(key)
            token = kstore.encrypt(self.parmsdb['DB_USER_PASSWORD'].encode(self.cpage))
            self.parmsdb['DB_USER_PASSWORD'] = 'ENC_' + token.decode(self.cpage)
            with open('config/config_db.yaml', 'w') as outfile:
                yaml.dump(self.parmsdb, outfile, default_flow_style=False)
                self.log.info('DB password was encripted')
        else:
            key = base64.urlsafe_b64encode(kdf.derive(self.parmsdb['SK'].encode(self.cpage)))
            kstore = Fernet(key)
        return kstore

    def _load_db_parms(self, lpatch=''):
        # ************* Load Parms
        with self.log.catch(onerror=lambda _: sys.exit(1)):
            with io.open(lpatch + 'config/config_db.yaml', encoding=self.cpage) as file:
                parms_db = yaml.load(file, Loader=yaml.FullLoader)
        return parms_db
