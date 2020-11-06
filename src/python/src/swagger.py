import io
import sys
import re
import yaml

from .__about__ import __version__
from .logconf import LoguruLogger


class LoadSwagger(LoguruLogger):
    def __init__(self, lpatch):
        super().__init__(lpatch)
        self.cpage = 'utf-8'
        self.version = __version__
        self.parms = self._load_assert_parms(lpatch)
        with self.log.catch(message='Error load swagger configuration', onerror=lambda _: sys.exit(1)):
            self._appy_assert()
        self.maxQueueSize = self.parms.get('maxQueueSize', 10000)
        self.ACCESS_LOG = self.parms.get('ACCESS_LOG', True)
        with self.log.catch(message='Error load swagger configuration', onerror=lambda _: sys.exit(1)):
            self.swagger_descriptions = self._prepare_doc(self.parms, lpatch)
        self.swagger_url = '/' + self.parms['URL'] + '/swagger'
        self.swaggerEnabled = self.parms.get('SWAGER_ENABLED', True)
        self.postOutField = self.parms.get('SPECIFICATIONS', {}).get('POST', {}).get('RESPONSE_FIELDS', {}).keys()
        self.apiurl = '/' + self.parms['URL'] + '/' + self.parms['SPECIFICATIONS']['VERSION']
        self.release = self.parms['SPECIFICATIONS']['SERVICE_DESCRITION']['RELEASE']
        self.log.info('Swagger initialized')

    def _load_assert_parms(self, lpatch):
        # ************* Load Parms
        with self.log.catch(onerror=lambda _: sys.exit(1)):
            with io.open(lpatch + 'config/config_service.yaml', encoding=self.cpage) as file:
                p = yaml.load(file, Loader=yaml.FullLoader)
        self.log.info('config_service.yaml loaded')
        return p

    def _appy_assert(self):
        for p in ['URL', 'ACCESS_LOG', 'MAX_FETCH_ROWS', 'SPECIFICATIONS']:
            if len(str(self.parms.get(p, ''))) < 1:
                self.log.critical('/config/config-service.yaml -> %s does not defined' % p)
                raise ValueError
        if self.parms.get('GET_ENABLED', False):
            if len(str(self.parms.get('SQL_GET', ''))) < 1:
                self.log.critical('/config/config-service.yaml -> %s does not defined' % 'SQL_GET')
                raise ValueError
        if self.parms.get('POST_ENABLED', False):
            if len(str(self.parms.get('PROC_POST', ''))) < 1:
                self.log.critical('/config/config-service.yaml -> %s does not defined' % 'PROC_POST')
                raise ValueError

    @staticmethod
    def _find(element: str, fdict):
        paths = element.replace('${', '').replace('}', '').split(".")
        data = fdict
        for i in range(0, len(paths)):
            data = data.get(paths[i], {})
        return str(data)

    def _prepare_doc(self, parms, lpatch):

        with io.open(lpatch + 'config/swagger_template.yaml', encoding=self.cpage) as file:
            swagger_conf = file.read()

        repl_pattern = re.findall(r'\${[a-zA-Z._-]+}', str(swagger_conf))
        for p in repl_pattern:
            new_s = self._find(p, parms)
            self.log.debug('pattern find:' + p + ':' + new_s)
            swagger_conf = swagger_conf.replace(p, new_s)

        descritpion = yaml.load(swagger_conf, Loader=yaml.FullLoader)  # .load(file, Loader=yaml.FullLoader)
        self.log.info('swagger_template.yaml loaded')

        url = '/' + parms['URL'] + '/' + parms['SPECIFICATIONS']['VERSION'] + '/{message_idt}/{source_system}'
        if self.parms.get('GET_ENABLED', False):
            getfield = parms['SPECIFICATIONS']['GET']['INPUT_REQUIRED_FIELDS']
            for f in getfield:
                descritpion['paths'][url]['get']['parameters'].append(
                    {'in': 'query', 'name': f, 'description': getfield[f], 'required': True,
                     'schema': {'type': 'string'}}
                )
            getfield = parms['SPECIFICATIONS']['GET']['RESPONSE_FIELDS']
            descritpion['components']['schemas']['get_required_out']['properties']['records']['required'] = []
            descritpion['components']['schemas']['get_required_out']['properties']['records']['properties'] = {}
            for f in getfield:
                descritpion['components']['schemas']['get_required_out']['properties']['records']['required'].append(f)
                descritpion['components']['schemas']['get_required_out']['properties']['records']['properties'][f] = \
                    {'type': 'string', 'example': 'value', 'description': getfield[f]}
        if self.parms.get('POST_ENABLED', False):
            postfield = parms['SPECIFICATIONS']['POST']['INPUT_REQUIRED_FIELDS']
            for f in postfield:
                descritpion['paths'][url]['post']['parameters'].append(
                    {'in': 'query', 'name': f, 'description': postfield[f], 'required': True,
                     'schema': {'type': 'string'}}
                )
            postfield = parms['SPECIFICATIONS']['POST']['RESPONSE_FIELDS']
            for f in postfield:
                descritpion['components']['schemas']['post_required_out']['required'].append(f)
                descritpion['components']['schemas']['post_required_out']['properties'][f] = \
                    {'type': 'string', 'example': postfield[f]}

        return descritpion
