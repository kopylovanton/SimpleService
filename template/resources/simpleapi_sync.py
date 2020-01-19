import io, sys

import yaml
from flask import Flask, Blueprint, current_app, url_for, jsonify
from flask_restplus import Api, fields, reqparse

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

class SimpeSyncApi(object):
    def __init__(self):
        self.cpage = 'utf-8'
        self.parms=self.__loadparms()
        self.__appyAssert()

        self.get_input_required_fields = self.parms['SPECIFICATIONS']['GET_DESCRITION']['INPUT_REQUIRED_FIELDS']
        self.get_responce_fields = self.parms['SPECIFICATIONS']['GET_DESCRITION']['RESPONCE_FIELDS']
        self.apiurl = '/' + self.parms['URL']+ '/' + self.parms['SPECIFICATIONS']['SERVICE_DESCRITION']['VERSION']

        from flask_restplus.apidoc import apidoc
        apidoc.url_prefix = self.apiurl

        # Base API URL <host>:<port>/<URL>/<VERSION>
        self.app = Flask(__name__)
        self.blueprint = Blueprint(self.parms['URL'], self.parms['SPECIFICATIONS']['SERVICE_DESCRITION']['TITLE'],
                              url_prefix=self.apiurl)
        self.api = self.simpleApi()
        self.app.register_blueprint(self.blueprint)

        self.get_input_parser=self.__get_input_parser()
        self.status_check_model = self.__status_check_model()
        self.get_responce_model = self.__get_responce_model()

    def __loadparms(self):
        # ************* Load Parms
        with io.open(r'config/config_get.yaml', encoding=self.cpage) as file:
            p = yaml.load(file, Loader=yaml.FullLoader)
        return p
    def __appyAssert(self):
        for p in ['URL', 'LOG_LEVEL', 'SQL_GET', 'MAX_FETCH_ROWS', 'SPECIFICATIONS']:
            assert len(str(self.parms[p])) > 1, '/config/config_get.yaml -> %s does not defined' % p
    def simpleApi(self):

        api = Api(self.blueprint, version=self.parms['SPECIFICATIONS']['SERVICE_DESCRITION']['VERSION'], \
                  title=self.parms['SPECIFICATIONS']['SERVICE_DESCRITION']['TITLE'], \
                  doc='/swagger',
                  description=self.parms['SPECIFICATIONS']['SERVICE_DESCRITION']['DESCRITION'],
                  default=self.parms['URL'], default_label='Specification')
        return api
    def __get_input_parser(self):
        # Request fields
        get_input_parser = reqparse.RequestParser()
        for i in self.get_input_required_fields:
            get_input_parser.add_argument(i, type=str, help=self.get_input_required_fields[i])
        return get_input_parser

    # Responce fields and model

    def __get_responce_model(self):
        return self.api.model(self.parms['URL'], {
        'rc': fields.Integer(required=True, description='Responce code'),
        'message': fields.String(required=True, description='Responce message'),
        'source_system': fields.String(required=True, description='Surce system IDT for logging'),
        'uid': fields.String(required=True, description='Unique message idt'),
        'input_parms': fields.Nested(self.api.model('get_input_parms',
                                               {i: fields.String(description=self.get_input_required_fields[i]) for i in
                                                self.get_input_required_fields})),
        'records': fields.List(fields.Nested(self.api.model('get_responce_record',
                                                       {i: fields.String(description=self.get_responce_fields[i]) for i in
                                                        self.get_responce_fields})))})
    def __status_check_model(self):
        # get status API
        return self.api.model('Status_Check', {
            'rc': fields.Integer(required=True, description='Responce code'),
            'message': fields.String(required=True, description='Responce message'),
            'db_status': fields.String(required=True, description='DB connection status UP/DOWN'),
            'up_time_min': fields.String(required=True, description='worker up time in minutes'),
            'getCount': fields.String(required=True,
                                      description='Count get request in last %s minutes' % (self.parms['statDepts'])),
            'meanGetDuration': fields.String(required=True,
                                             description='Mean durations get request in last %s minutes' % (
                                                 self.parms['statDepts'])),
            'errorsCount': fields.String(required=True,
                                         description='Errors count in last %s minutes' % (self.parms['statDepts']))})
