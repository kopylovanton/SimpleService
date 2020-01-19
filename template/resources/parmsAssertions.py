import io
import yaml
from datetime import datetime
import re

class pAssertion(object):
    def __init__(self, logging, enccp='utf-8'):
        self.log = logging
        self.cpage = enccp
        parms=self.__load_parms()

        self.parms_assertions = {}
        self.formats_assertions = {}
        for tp in ['GET']:
            self.parms_assertions[tp]=parms.get('ASSERTIONS_PARMS',{}).get(tp,{})
            self.parms_assertions[tp] = {p: self.parms_assertions[tp][p] for p in self.parms_assertions[tp] if len(p)>0}
            self.log.info('Load %s %s PARMS assertions' % (len (self.parms_assertions[tp]) , tp))

            self.formats_assertions[tp]=parms.get('ASSERTIONS_FORMATS',{}).get(tp,{})
            self.formats_assertions[tp] = {p:self.formats_assertions[tp][p] for p in self.formats_assertions[tp] if len(p)>0}
            self.log.info('Load %s %s FORMAT assertions' % (len (self.formats_assertions[tp]) , tp))

    def chekAssertions(self,parms, req_type, uid='internal'):
        ''' Check paramets aseertions loaded from config file config/config_get.yaml'''

        resp={'rc' : 200, 'message' :'ok'}
        # Check in list assertions
        passert = (p for p in parms if p in self.parms_assertions[req_type])
        for p in passert:
            if parms[p] not in self.parms_assertions[req_type][p]:
                return {'rc' : 412, 'message' :'Inward parameter %s does not in allowed list' % p}

        # Formats assertions
        passert = (p for p in parms if p in self.formats_assertions[req_type])
        for p in passert:
            fa = self.formats_assertions[req_type][p]
            if fa.find('date=')==0:
                try:
                    d=datetime.strptime( parms[p], fa[5:])
                except:
                    resp = {'rc': 412, 'message': 'Inward parameter %s does not pass format assertion %s' % (p,fa)}
            elif fa.find('re=') == 0:
                try:
                    if re.fullmatch( fa[3:] , parms[p]) == None:
                        resp = {'rc': 412,
                                'message': 'Inward parameter %s does not pass format assertion %s' % (p, fa)}
                except:
                    resp = {'rc': 412, 'message': 'Inward parameter %s does not pass format assertion %s' % (p,fa)}
        if resp['rc']==412:
            self.log.warning('Assertion error for UID %s, %s' % (uid,resp['message']))
        return resp

    def __load_parms(self):
        # ************* Load Parms
        with io.open(r'config/config_get.yaml', encoding=self.cpage) as file:
            parms = yaml.load(file, Loader=yaml.FullLoader)
        return parms