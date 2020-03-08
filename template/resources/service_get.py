# ************* Import
import logging
import time

import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property

from flask import  request
from flask_restplus import Resource


from .__about__ import __version__
from .db_connection_oracle import Oracle as db_connections
from .wsstats import WSStatistic
from .parmsAssertions import pAssertion
from .simpleapi_sync import SimpeSyncApi
from .cust_preprocess import inward_parms_preprocessing
from .cust_postprocess import outward_parms_preprocessing

# ************* Flask Api
simple_app = SimpeSyncApi()
serviseStat = WSStatistic(simple_app.parms.get('statDepts',5))

# ************* Logging
logFormat = '%(asctime)s =%(levelname)s= [%(name)s-%(lineno)d] - %(message)s'
logging.basicConfig(format=logFormat, level=logging.ERROR)

log = logging.getLogger(simple_app.parms['URL'])
log.setLevel(simple_app.parms['LOG_LEVEL'])
log.info('Start process worker at URL = <host>:<port>%s , template version: %s , configurations release %s' %
         (simple_app.apiurl , __version__,simple_app.release))

# Open Oracle connections
ora = db_connections(log)
# Load assertions
pAssertion = pAssertion(log)


@simple_app.api.route('/<string:source_system>/<string:message_idt>')
@simple_app.api.doc(params={'source_system': 'Surce system IDT for logging',
                 'message_idt': 'Unique message idt'})
class stableApi(Resource):
    """ Base api for get, put, udate operaions """

    @simple_app.api.doc(description=simple_app.parms['SPECIFICATIONS']['GET_DESCRITION']['DESCRITION']+
                      '\n Assertions list: %s' % pAssertion.parms_assertions.get('GET','NONE') +
                      '\n Assertions format: %s' % pAssertion.formats_assertions.get('GET','NONE'),
             responses={500: 'Some problem with DB or SQL',
                        412: 'Failed assertion for inward parameters'},
             params=simple_app.get_input_required_fields)
    @simple_app.api.marshal_with(simple_app.get_responce_model)
    def get(self, source_system, message_idt):
        # try:
        start_time = time.time()
        args = simple_app.get_input_parser.parse_args()
        ipadr = request.remote_addr
        log.info('Message IDT:%s, from SYSTEM <%s>, IP <%s> , started with input parameters: %s' %
                 (message_idt, source_system, ipadr, str(args)))
        # Assertion
        adict = args.copy()
        adict['source_system']=source_system
        buf = pAssertion.chekAssertions(adict,'GET',message_idt)
        if buf['rc'] == 200:
            args=inward_parms_preprocessing(args,log,simple_app.parms)
            ora.execute(simple_app.parms['SQL_GET'], bindvars=args, uid=message_idt,fetch=True,fetchcount=simple_app.parms['MAX_FETCH_ROWS'])
            buf = ora.data
            buf['records']=outward_parms_preprocessing(buf.get('records',[]),log,simple_app.parms)
        else:
            buf['records'] = []

        buf['input_parms'] = args
        buf['source_system'] = source_system
        buf['message_idt'] = message_idt

        dtime = round(time.time() - start_time, 4)
        if buf['rc']==200:
            serviseStat.putGetItem(dtime)
        else:
            serviseStat.putErrItem()
        log.info("Message IDT:%s, processed in --- %s seconds ---" % (message_idt, dtime))
        return buf, buf['rc']
    # except:
    # return 'Server internal error', 500

@simple_app.api.route('/status')
class statusApi(Resource):
    """ Base api for get, put, udate operaions """

    @simple_app.api.doc(description='Health checks and status information')
    @simple_app.api.marshal_with(simple_app.status_check_model)
    def get(self):
        # try:
        start_time = time.time()
        ipadr = request.remote_addr
        log.info('Health check request, from IP <%s>' % (ipadr))
        dbIsConnect = ora.db_is_connect()
        buf = ora.data
        if dbIsConnect:
            buf['db_status'] = 'UP'
        else:
            buf['db_status'] = 'DOWN'
        buf['rc'] = 200
        stat = serviseStat.getStat()
        for i in stat:
            buf[i] = stat[i]
        log.info("Health check request, from IP <%s>, processed in --- %s seconds ---" % (
        ipadr, round(time.time() - start_time, 4)))
        return buf, buf['rc']
