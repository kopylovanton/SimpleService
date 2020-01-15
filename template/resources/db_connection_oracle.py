# ************* Import
import cx_Oracle
import time
import os
import io
import yaml
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ************* Oracle connection
class Oracle(object):

    def __init__(self, logging, enccp='utf-8'):
        self.cpage = enccp
        self.__connected = False
        self.log = logging

        self.parmsdb=self.__load_parms();
        for p in ['DB_CONN_STRING', 'DB_USER_NAME', 'DB_USER_PASSWORD','DB_ENCODING','CURRENT_SCHEMA','DB_EXECUTE_TIMEOUT']:
            assert len(str(self.parmsdb[p])) > 1, '/config/configdb.yaml -> %s does not defined' % p
        self.kstore=self.__kstore()

        self.username = self.parmsdb['DB_USER_NAME']
        self.pwd = self.parmsdb['DB_USER_PASSWORD'][4:]
        self.conn_string = self.parmsdb['DB_CONN_STRING']
        self.encoding = self.parmsdb['DB_ENCODING']
        self.current_schema = self.parmsdb['CURRENT_SCHEMA']
        self.callTimeout = self.parmsdb['DB_EXECUTE_TIMEOUT']


        try:
            self.db = cx_Oracle.connect(self.username, self.get_password(), self.conn_string, encoding=self.encoding)
            self.data = {'rc': 200, 'message': 'DB connected'}
            self.db.current_schema = self.current_schema
            self.db.callTimeout = self.callTimeout
            self.__connected = True
            self.log.info('DB <%s> connection started' % (self.conn_string))
        except cx_Oracle.DatabaseError as e:
            errorObj, = e.args
            self.log.error('DB <%s> have not connected.  Oracle error message: ' % (self.conn_string)) + str(
                errorObj.message)
            raise

    def __del__(self):
        self.disconnect()
    def get_password(self):
        return self.kstore.decrypt(self.pwd.encode(self.cpage)).decode(self.cpage)

    def connect(self, uid='internal'):
        """ Connect to the database. """
        try:
            self.db = cx_Oracle.connect(self.username, self.get_password(), self.conn_string, encoding=self.encoding)
            # If the database connection succeeded create the cursor
            # we-re going to use.
            self.data = {'rc': 200, 'message': 'DB connected'}
            self.__connected = True
            self.db.current_schema = self.current_schema
            self.db.callTimeout = self.callTimeout
            self.log.info('Message UID:%s - DB <%s> connection started' % (uid, self.conn_string))
        except cx_Oracle.DatabaseError as e:
            errorObj, = e.args
            self.data = {'rc': 500, 'message': 'Can not connect to DB . Oracle error message: ' + str(errorObj.message)}
            self.__connected = False
            self.log.error(
                'Message UID:%s - Can not connect to DB <%s>. Oracle error message: ' % (uid, self.conn_string) + str(
                    errorObj.message))

    def disconnect(self):
        """
        Disconnect from the database. If this fails, for instance
        if the connection instance doesn't exist, ignore the exception.
        """
        try:
            self.cursor.close()
            self.db.close()
            self.__connected = False
            self.log.info('DB <%s> connection finished' % (self.conn_string))
        except:
            pass

    def execute(self, sql, bindvars={}, commit=False, uid='unknown'):
        """
        Execute whatever SQL statements are passed to the method;
        commit if specified. Do not specify fetchall() in here as
        the SQL statement may not be a select.
        bindvars is a dictionary of variables you pass to execute.
        """
        # if sql.lower.find('')
        start_time = time.time()
        if not self.__connected:
            self.connect(uid=uid)
        if self.__connected:
            try:
                self.cursor = self.db.cursor()
                self.cursor.execute(sql, bindvars)
                self.data = {'rc': 200, 'message': 'ok'}
                # Only commit if it-s necessary.
                if commit:
                    self.db.commit()
                self.log.info(
                    "Message UID:%s, SQL executed in --- %s seconds ---" % (uid, round(time.time() - start_time, 4)))

            except cx_Oracle.DatabaseError as e:
                errorObj, = e.args
                self.data = {'rc': 500,
                             'message': 'Can not execute SQL. Oracle error message: ' + str(errorObj.message)}
                self.__connected = False
                self.log.error(
                    'Message UID:%s - Can not execute SQL . Oracle error message: ' % (uid) + str(errorObj.message))

    def __db_not_connect(self):
        """ Check DB status """
        try:
            self.cursor = self.db.cursor()
            self.cursor.execute('select 0 from dual')
            self.cursor.close()
            self.data = {'rc': 200, 'message': 'DB <%s> connection UP' % (self.conn_string)}
            self.__connected = True
            return False
            self.log.info('Status DB <%s> DB <%s> connection UP' % (self.conn_string))
        except:
            self.data = {'rc': 500, 'message': 'DB <%s> connection DOWN' % (self.conn_string)}
            self.__connected = False
            self.log.info('Status DB <%s> connection DOWN' % (self.conn_string))
            return True

    def db_is_connect(self):
        """ Check DB status """
        return (not self.__db_not_connect())
        # ************* check DB pass
    def __kstore(self):
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
            with open('config/configdb.yaml', 'w') as outfile:
                yaml.dump(self.parmsdb, outfile, default_flow_style=False)
                self.log.info('DB password was encripted')
        else:
            key = base64.urlsafe_b64encode(kdf.derive(self.parmsdb['SK'].encode(self.cpage)))
            kstore = Fernet(key)
        return kstore
    def __load_parms(self):
        # ************* Load Parms
        with io.open(r'config/configdb.yaml', encoding=self.cpage) as file:
            parmsdb = yaml.load(file, Loader=yaml.FullLoader)
        return parmsdb


