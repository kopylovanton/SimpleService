# ************* Import
import cx_Oracle
import time
from resources import kstore
# ************* Oracle connection
class Oracle(object):

    def __init__(self, username, pas, conn_string, enc, logging, current_schema, enccp='utf-8'):
        self.username = username
        self.pwd = pas
        self.conn_string = conn_string
        self.encoding = enc
        self.__connected = False
        self.log=logging
        self.cpage=enccp
        self.current_schema =current_schema
        try:
            self.db = cx_Oracle.connect(self.username, self.get_password(), self.conn_string, encoding=self.encoding)
            self.data = {'rc': 200, 'message': 'DB connected'}
            self.db.current_schema =self.current_schema
            self.__connected = True
            self.log.info('DB <%s> connection started' % (self.conn_string))
        except cx_Oracle.DatabaseError as e:
            errorObj, = e.args
            self.log.error('DB <%s> have not connected.  Oracle error message: ' %  (self.conn_string)) + str(errorObj.message)
            raise

    def __del__(self):
        self.disconnect()

    def get_password(self):
        return kstore.decrypt(self.pwd.encode(self.cpage)).decode(self.cpage)
    def connect(self,uid='internal'):
        """ Connect to the database. """
        try:
            self.db = cx_Oracle.connect(self.username, self.get_password(), self.conn_string, encoding=self.encoding)
            # If the database connection succeeded create the cursor
            # we-re going to use.
            self.data = {'rc': 200, 'message': 'DB connected'}
            self.__connected = True
            self.db.current_schema = self.current_schema
            self.log.info('Message UID:%s - DB <%s> connection started' % (uid, self.conn_string))
        except cx_Oracle.DatabaseError as e:
            errorObj, = e.args
            self.data = {'rc': 500, 'message': 'Can not connect to DB . Oracle error message: ' + str(errorObj.message)}
            self.__connected = False
            self.log.error('Message UID:%s - Can not connect to DB <%s>. Oracle error message: '%(uid, self.conn_string) + str(errorObj.message))

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
        #if sql.lower.find('')
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
                self.log.info("Message UID:%s, SQL executed in --- %s seconds ---" % (uid, round(time.time() - start_time,4)))

            except cx_Oracle.DatabaseError as e:
                errorObj, = e.args
                self.data = {'rc': 500, 'message': 'Can not execute SQL. Oracle error message: ' + str(errorObj.message) }
                self.__connected = False
                self.log.error('Message UID:%s - Can not execute SQL . Oracle error message: ' % (uid) + str(errorObj.message))

    def __db_not_connect(self):
        """ Check DB status """
        try:
            self.cursor = self.db.cursor()
            self.cursor.execute('select 0 from dual')
            self.cursor.close()
            self.data = {'rc': 200, 'message': 'DB <%s> connection UP' % (self.conn_string)}
            self.__connected = True
            return False
            log.info('Status DB <%s> DB <%s> connection UP' % (self.conn_string))
        except:
            self.data = {'rc': 500, 'message': 'DB <%s> connection DOWN' % (self.conn_string) }
            self.__connected = False
            log.info('Status DB <%s> connection DOWN' % (self.conn_string))
            return True

    def db_is_connect(self):
        """ Check DB status """
        return (not self.__db_not_connect())
