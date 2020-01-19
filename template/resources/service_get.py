# ************* Import
import logging
import time

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
log.info('Start process worker at URL = <host>:<port>/%s/%s , version: %s  ' %
         (simple_app.parms['URL'],simple_app.parms['SPECIFICATIONS']['SERVICE_DESCRITION']['VERSION'] , __version__))

# Open Oracle connections
ora = db_connections(log)
# Load assertions
pAssertion = pAssertion(log)


@simple_app.api.route('/<string:source_system>/<string:uid>')
@simple_app.api.doc(params={'source_system': 'Surce system IDT for logging',
                 'uid': 'Unique message idt'})
class stableApi(Resource):
    """ Base api for get, put, udate operaions """

    @simple_app.api.doc(description=simple_app.parms['SPECIFICATIONS']['GET_DESCRITION']['DESCRITION']+
                      '\n Assertions list: %s' % pAssertion.parms_assertions.get('GET','NONE') +
                      '\n Assertions format: %s' % pAssertion.formats_assertions.get('GET','NONE'),
             responses={500: 'Some problem with DB or SQL'},
             params=simple_app.get_input_required_fields)
    @simple_app.api.marshal_with(simple_app.get_responce_model)
    def get(self, source_system, uid):
        # try:
        start_time = time.time()
        args = simple_app.get_input_parser.parse_args()
        ipadr = request.remote_addr
        log.info('Message UID:%s, from SYSTEM <%s>, IP <%s> , started with input parameters: %s' %
                 (uid, source_system, ipadr, str(args)))
        # Assertion
        adict = args.copy()
        adict['source_system']=source_system
        buf = pAssertion.chekAssertions(adict,'GET',uid)
        if buf['rc'] == 200:
            args=inward_parms_preprocessing(args,log)
            ora.execute(simple_app.parms['SQL_GET'], bindvars=args, uid=uid,fetch=True,fetchcount=simple_app.parms['MAX_FETCH_ROWS'])
            buf = ora.data
            buf['records']=outward_parms_preprocessing(buf['records'],log)
        else:
            buf['records'] = []

        buf['input_parms'] = args
        buf['source_system'] = source_system
        buf['uid'] = uid

        dtime = round(time.time() - start_time, 4)
        if buf['rc']==200:
            serviseStat.putGetItem(dtime)
        else:
            serviseStat.putErrItem()
        log.info("Message UID:%s, processed in --- %s seconds ---" % (uid, dtime))
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
