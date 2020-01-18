# ************* Import
import io
import logging
import sys
import time

import yaml
from flask import Flask, request, Blueprint, current_app, url_for, jsonify
from flask_restplus import Api, Resource, fields, reqparse

from .__about__ import __version__
from .db_connection_oracle import Oracle as db_connections
from .wsstats import WSStatistic
from .parmsAssertions import pAssertion

cpage = 'utf-8'

# ************* Load Parms
with io.open(r'config/config_get.yaml', encoding=cpage) as file:
    parms = yaml.load(file, Loader=yaml.FullLoader)

for p in ['URL', 'LOG_LEVEL', 'SQL_GET', 'MAX_FETCH_ROWS', 'SPECIFICATIONS']:
    assert len(str(parms[p])) > 1, '/config/config_get.yaml -> %s does not defined' % p

# Base API URL <host>:<port>/<URL>/<VERSION>
apiurl = '/' + parms['URL']+ '/' + parms['SPECIFICATIONS']['SERVICE_DESCRITION']['VERSION']

# ************* Logging
logFormat = '%(asctime)s =%(levelname)s= [%(name)s-%(lineno)d] - %(message)s'
# loghandler = TimedRotatingFileHandler("logfile",when="midnight")
logging.basicConfig(format=logFormat, level=logging.ERROR)

log = logging.getLogger(parms['URL'])
log.setLevel(parms['LOG_LEVEL'])
log.info('Start process worker at URL = <host>:<port>/%s/%s , version: %s  ' %
         (parms['URL'],parms['SPECIFICATIONS']['SERVICE_DESCRITION']['VERSION'] , __version__))

# Open Oracle connections
ora = db_connections(log)
# Load assertions
pAssertion = pAssertion(log)

# Ensure the specs endpoint is not treated as an "external" resource.
@property
def fix_specs_url(self):
    return url_for(self.endpoint('specs'), _external=False)
Api.specs_url = fix_specs_url

# Ensure exceptions are picked up, API responses are produced as expected, and
# exceptions are written to the log. Logging code taken from flask_restplus error handler:
# https://flask-restplus.readthedocs.io/en/stable/_modules/flask_restplus/api.html#Api.handle_error
def return_error(e):
    # I return a custom JSON object here. But do what you want.
    return (jsonify({'rc': 404, 'message': 'Can not find resources: ' + str(e.__repr__)}))

def fix_error_router(self, original_handler, e):
    exc_info = sys.exc_info()
    if exc_info[1] is None:
        exc_info = None
    if (exc_info):
        current_app.log_exception(exc_info)
    else:
        current_app.logger.error(str(e))
    return return_error(e)

Api.error_router = fix_error_router

# Import apidoc for url resources patching
from flask_restplus.apidoc import apidoc

# Make a global change setting the URL prefix for the swaggerui at the module level
apidoc.url_prefix = apiurl

# ************* Flask Api

serviseStat = WSStatistic(parms['statDepts'])

app = Flask(__name__)

blueprint = Blueprint(parms['URL'], parms['SPECIFICATIONS']['SERVICE_DESCRITION']['TITLE'],
                      url_prefix=apiurl)

# from werkzeug.middleware.proxy_fix import ProxyFix
# app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

api = Api(blueprint, version=parms['SPECIFICATIONS']['SERVICE_DESCRITION']['VERSION'], \
          title=parms['SPECIFICATIONS']['SERVICE_DESCRITION']['TITLE'], \
          doc='/swagger',
          description=parms['SPECIFICATIONS']['SERVICE_DESCRITION']['DESCRITION']  ,
          default=parms['URL'], default_label='Specification')
app.register_blueprint(blueprint)

# Request fields
get_input_required_fields = parms['SPECIFICATIONS']['GET_DESCRITION']['INPUT_REQUIRED_FIELDS']
get_input_parser = reqparse.RequestParser()
for i in get_input_required_fields:
    get_input_parser.add_argument(i, type=str, help=get_input_required_fields[i])

# Responce fields and model
get_responce_fields = parms['SPECIFICATIONS']['GET_DESCRITION']['RESPONCE_FIELDS']

get_responce_model = api.model(parms['URL'], {
    'rc': fields.Integer(required=True, description='Responce code'),
    'message': fields.String(required=True, description='Responce message'),
    'source_system': fields.String(required=True, description='Surce system IDT for logging'),
    'uid': fields.String(required=True, description='Unique message idt'),
    'input_parms': fields.Nested(api.model('get_input_parms',
                                           {i: fields.String(description=get_input_required_fields[i]) for i in
                                            get_input_required_fields})),
    'records': fields.List(fields.Nested(api.model('get_responce_record',
                                                   {i: fields.String(description=get_responce_fields[i]) for i in
                                                    get_responce_fields})))})


# ns = api.namespace(parms['URL'], description=parms['SPECIFICATIONS']['SERVICE_DESCRITION']['DESCRITION'],ordered=False)

@api.route('/<string:source_system>/<string:uid>')
@api.doc(params={'source_system': 'Surce system IDT for logging',
                 'uid': 'Unique message idt'})
class stableApi(Resource):
    """ Base api for get, put, udate operaions """

    @api.doc(description=parms['SPECIFICATIONS']['GET_DESCRITION']['DESCRITION']+
                      '\n Assertions list: %s' % pAssertion.parms_assertions.get('GET','NONE') +
                      '\n Assertions format: %s' % pAssertion.formats_assertions.get('GET','NONE'),
             responses={500: 'Some problem with DB or SQL'},
             params=get_input_required_fields)
    @api.marshal_with(get_responce_model)
    def get(self, source_system, uid):
        # try:
        start_time = time.time()
        args = get_input_parser.parse_args()
        ipadr = request.remote_addr
        log.info('Message UID:%s, from SYSTEM <%s>, IP <%s> , started with input parameters: %s' %
                 (uid, source_system, ipadr, str(args)))
        # Assertion
        adict = args.copy()
        adict['source_system']=source_system
        buf = pAssertion.chekAssertions(adict,'GET',uid)
        if buf['rc'] == 200:
            ora.execute(parms['SQL_GET'], bindvars=args, uid=uid,fetch=True,fetchcount=parms['MAX_FETCH_ROWS'])
            buf = ora.data
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


# get status API
status_check_model = api.model('Status_Check', {
    'rc': fields.Integer(required=True, description='Responce code'),
    'message': fields.String(required=True, description='Responce message'),
    'db_status': fields.String(required=True, description='DB connection status UP/DOWN'),
    'up_time_min': fields.String(required=True, description='worker up time in minutes'),
    'getCount': fields.String(required=True, description='Count get request in last %s minutes' % (parms['statDepts'])),
    'meanGetDuration': fields.String(required=True, description='Mean durations get request in last %s minutes' % (
    parms['statDepts'])),
    'errorsCount': fields.String(required=True, description='Errors count in last %s minutes' % (parms['statDepts']))})


@api.route('/status')
class statusApi(Resource):
    """ Base api for get, put, udate operaions """

    @api.doc(description='Health checks and status information')
    @api.marshal_with(status_check_model)
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
