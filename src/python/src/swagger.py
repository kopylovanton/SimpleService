import io
import sys

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
        for p in ['URL', 'ACCESS_LOG', 'SQL_GET', 'MAX_FETCH_ROWS', 'SPECIFICATIONS']:
            if len(str(self.parms[p])) < 1:
                self.log.critical('/config/config-service.yaml -> %s does not defined' % p)
                raise

    def _prepare_doc(self, parms, lpatch):
        with self.log.catch(onerror=lambda _: sys.exit(1)):
            with io.open(lpatch + 'config/swagger_template.yaml', encoding=self.cpage) as file:
                descritpion = yaml.load(file, Loader=yaml.FullLoader)
        self.log.info('swagger_template.yaml loaded')

        url = '/%s/V1/{message_idt}/{source_system}' % self.parms['URL']

        getfield = parms.get('SPECIFICATIONS', {}).get('GET', {}).get('INPUT_REQUIRED_FIELDS', {})
        for f in getfield:
            descritpion['paths'][url]['get']['parameters'].append(
                {'in': 'query', 'name': f, 'description': getfield[f], 'required': True,
                 'schema': {'type': 'string'}}
            )
        postfield = parms.get('SPECIFICATIONS', {}).get('POST', {}).get('INPUT_REQUIRED_FIELDS', {})
        for f in postfield:
            descritpion['paths'][url]['post']['parameters'].append(
                {'in': 'query', 'name': f, 'description': postfield[f], 'required': True,
                 'schema': {'type': 'string'}}
            )
        postfield = parms.get('SPECIFICATIONS', {}).get('POST', {}).get('RESPONSE_FIELDS', {})
        for f in postfield:
            descritpion['components']['schemas']['post_required_out']['required'].append(f)
            descritpion['components']['schemas']['post_required_out']['properties'][f] = \
                {'type': 'string', 'example': postfield[f]}
        return descritpion
