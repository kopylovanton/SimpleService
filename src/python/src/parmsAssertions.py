import io
import re
import sys
from datetime import datetime

import yaml

from .logconf import LoguruLogger

class PAssertion(LoguruLogger):
    def __init__(self, lpatch, enccp='utf-8'):
        super().__init__(lpatch)
        self.cpage = enccp
        parms = self._load_service_parms(lpatch)
        self.parms_assertions = {}
        self.formats_assertions = {}
        self.required_fields = {}
        self.allowedReqType = ['GET', 'POST']
        self.log.info('Assertions initialized')

        for req_type in self.allowedReqType:
            self.required_fields[req_type] = parms.get('SPECIFICATIONS', {}). \
                get(req_type, {}). \
                get('INPUT_REQUIRED_FIELDS', {})

            self.parms_assertions[req_type] = parms.get('ASSERTIONS_PARMS', {}).get(req_type, {})
            self.parms_assertions[req_type] = {p: self.parms_assertions[req_type][p] for p in
                                               self.parms_assertions.get(req_type, []) if len(p) > 0}
            self.log.info('Load %s %s PARMS assertions' % (len(self.parms_assertions[req_type]), req_type))

            self.formats_assertions[req_type] = parms.get('ASSERTIONS_FORMATS', {}).get(req_type, {})
            self.formats_assertions[req_type] = {p: self.formats_assertions[req_type][p] for p in
                                                 self.formats_assertions.get(req_type, []) if len(p) > 0}
            self.log.info('Load %s %s FORMAT assertions' % (len(self.formats_assertions[req_type]), req_type))

    def chek_assertions(self, inparms, req_type):
        """ Check paramets aseertions loaded from config file config/config_get.yaml"""
        if inparms['rc'] != 200:
            return inparms
        if req_type not in self.allowedReqType:
            inparms['rc'] = 412
            inparms['message'] = 'Request type %s does not allow' % req_type
            return inparms

        parms = inparms['input_parms'].copy()
        parms['source_system'] = inparms['source_system']
        # Check input parms is present
        for f in self.required_fields.get(req_type, []):
            if parms.get(f, None) is None:
                inparms['rc'] = 412
                inparms['message'] = 'Inward parameter %s does not find in input parameters' % f

        for f in parms:
            if self.required_fields.get(req_type, []).get(f, None) is None and f != 'source_system':
                inparms['rc'] = 412
                inparms['message'] = 'Illegal parameter name: %s' % f
        # Check in assertions list
        passert = [p for p in parms if p in self.parms_assertions.get(req_type, [])]
        for p in passert:
            if parms[p] not in self.parms_assertions[req_type][p]:
                inparms['rc'] = 412
                inparms['message'] = 'Inward parameter %s does not in allowed list' % p
                return inparms

        # Formats assertions
        passert = (p for p in parms if p in self.formats_assertions.get(req_type, []))
        for p in passert:
            fa = self.formats_assertions[req_type][p]
            if fa.find('date=') == 0:
                try:
                    _ = datetime.strptime(parms[p], fa[5:])
                except ValueError:
                    inparms['rc'] = 412
                    inparms['message'] = 'Inward parameter %s does not pass format assertion %s' % (p, fa)
            elif fa.find('re=') == 0:
                if re.fullmatch(fa[3:], parms[p]) is None:
                    inparms['rc'] = 412
                    inparms['message'] = 'Inward parameter %s does not pass format assertion %s' % (p, fa)
        if inparms['rc'] == 412:
            self.log.warning('Assertion error for Message IDT %s, %s' % (inparms['message_idt'], inparms['message']))
        return inparms

    def _load_service_parms(self, lpatch):
        # ************* Load Parms
        with self.log.catch(message='Error loading config_service.yaml',onerror=lambda _: sys.exit(1)):
            with io.open(lpatch + 'config/config_service.yaml', encoding=self.cpage) as file:
                parms = yaml.load(file, Loader=yaml.FullLoader)
        return parms
