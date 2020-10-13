import time

from aiohttp import web

from .cust_postprocess import outward_parms_preprocessing
from .cust_preprocess import inward_parms_preprocessing
from .oracle_connection import Oracle
from .parmsAssertions import PAssertion
from .swagger import LoadSwagger
from .wsstats import WSStatistic


class ApiHandler(LoadSwagger, WSStatistic, PAssertion, Oracle):
    def __init__(self, lpatch):
        super().__init__(lpatch)
        self.GetTotalDurationMean = 0.001
        self.PostTotalDurationMean = 0.001
        self.lastGetStat = time.time()
        self.qsize = 0

    # preprocess
    def base_request(self, request):
        data = {'message_idt': request.match_info.get('message_idt', 'unknown'),
                'source_system': request.match_info.get('source_system', 'unknown'),
                'rc': 200,
                'message': 'Success',
                'input_parms': {c: request.query[c] for c in request.query},
                }
        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            cli_ip = str(peername[0])
        else:
            cli_ip = 'ip?'
        # qsize = self.dbExecutor._work_queue.qsize()

        # GET Assertions
        if 'unknown' in [data['message_idt'], data['source_system']]:
            data['rc'] = 400
            data['message'] = 'message_idt or source_system not provided'
        if data['rc'] == 200:
            maxqsize = round(self.connPolSize * (self.callTimeout / (1000 * (self.StatSQLDurationMean + 0.0001))))
            if self.qsize > maxqsize:
                self.log.warning(
                    ('Message IDT:%s;queue size %s is too big. Recommended size less %s.'
                     'Try add DB connection pool size in config-db.cfg') %
                    (data['message_idt'], self.qsize, maxqsize))
        if self.qsize > self.maxQueueSize:
            data['rc'] = 429
            data['message'] = 'Too Many Requests'
        if data['rc'] == 200:
            a_resp = self.chek_assertions(data.copy(), request.method)
            data['rc'] = a_resp['rc']
            data['message'] = a_resp['message']
        if data['rc'] == 200:
            data['input_parms'] = inward_parms_preprocessing(request.method, data['input_parms'], self.parms)
        return data, cli_ip

    # GET
    async def get_record(self, request):
        self.qsize += 1
        start_time = time.time()
        sqld = '-'
        data, cli_ip = self.base_request(request)
        data['records'] = []
        # GET DB Call
        if data['rc'] == 200:
            fparms = (self.parms['SQL_GET'],
                      data['input_parms'],
                      data['message_idt'],
                      self.parms['MAX_FETCH_ROWS'])
            self.set_thread_pool_executor()
            db_resp = await request.loop.run_in_executor(self.dbExecutor, self.sync_sql, *fparms)
            data['rc'] = db_resp['rc']
            data['message'] = db_resp['message']
            data['records'] = db_resp['records']
            data = outward_parms_preprocessing(request.method, data, self.parms)
            sqld = db_resp['sqld']
            # except asyncio.TimeoutError:
            #     data['rc'] = 408
            #     data['message'] = 'Timeout'

        dtime = round(time.time() - start_time, 4)
        self.GetTotalDurationMean = round((1.8 * self.GetTotalDurationMean + 0.2 * dtime) / 2, 4)
        logmsg = ('%s: [IDT:%s] [rc:%s; %s] [Queue:%s] [Request Total/SQL:%s/%s] '
                  '[Mean Total/SQL:%s/%s] [SYSTEM:<%s>] [IP:<%s>] [input parms: %s]') % \
                 (request.method, data['message_idt'], data['rc'], data['message'], self.qsize, dtime, sqld,
                  self.GetTotalDurationMean, self.StatSQLDurationMean,
                  data['source_system'], cli_ip, request.query)
        if data['rc'] == 200:
            self.log.info(logmsg)
        else:
            self.log.warning(logmsg)
        self.calc_stat(data['rc'])
        self.qsize -= 1
        return web.json_response(data, status=data['rc'])

    # POST
    async def post_record(self, request):
        self.qsize += 1
        start_time = time.time()
        sqld = '-'
        data, cli_ip = self.base_request(request)

        # DB Call
        if data['rc'] == 200:
            fparms = (self.parms['PROC_POST'],
                      data['input_parms'],
                      self.postOutField,
                      data['message_idt'])
            self.set_thread_pool_executor()
            db_resp = await request.loop.run_in_executor(self.dbExecutor, self.sync_plsql, *fparms)
            data['rc'] = db_resp['rc']
            data['message'] = db_resp['message']
            for f in self.postOutField:
                data[f] = db_resp.get(f, '')
            data = outward_parms_preprocessing(request.method, data, self.parms)
            sqld = db_resp['sqld']

        dtime = round(time.time() - start_time, 4)
        self.PostTotalDurationMean = round((1.8 * self.PostTotalDurationMean + 0.2 * dtime) / 2, 4)
        logmsg = ('%s: [IDT:%s] [rc:%s; %s] [Queue:%s] [Request Total/PLSQL:%s/%s] [Mean Total/PLSQL:%s/%s] '
                  '[SYSTEM:<%s>] [IP:<%s>] [input parms: %s]') % \
                 (request.method, data['message_idt'], data['rc'], data['message'], self.qsize, dtime, sqld,
                  self.PostTotalDurationMean, self.StatPLSQLDurationMean,
                  data['source_system'], cli_ip, request.query)
        if data['rc'] == 200:
            self.log.info(logmsg)
        else:
            self.log.warning(logmsg)
        self.calc_stat(data['rc'])
        self.qsize -= 1
        return web.json_response(data, status=data['rc'])

    # GET Service Status
    async def get_stat(self, request):
        """calculate statistics"""
        if not self.db_connected:
            self.db_connect()
        if round((time.time() - self.lastGetStat) / 60, 1) > 5:
            self.set_thread_pool_executor()
            db_state = await request.loop.run_in_executor(self.dbExecutor, self.db_is_connect)
            self.lastGetStat = time.time()
        else:
            db_state = self.db_connected
        if db_state:
            db_state_str = 'UP'
        else:
            db_state_str = 'Down'
        stat = {
            'rc': 200,
            'message': 'Service is up',
            'dbConnectionStatus': db_state_str,
            'upTimeInMin': round((time.time() - self.StatstartStatTime) / 60, 1),
            'lastSuccessInMin': round((time.time() - self.StatlastSuccess) / 60, 1),
            'lastErrorInMin': round((time.time() - self.StatlastError) / 60, 1),
            'meanGetTotalDurationInSec': self.GetTotalDurationMean,
            'meanPostTotalDurationInSec': self.PostTotalDurationMean,
            'meanGetSQLDurationInSec': self.StatSQLDurationMean,
            'meanPostPLSQLDurationInSec': self.StatPLSQLDurationMean,
            'workQueue': self.qsize,
            'maxConfQueue': self.maxQueueSize,
            'dbConfConPool': self.connPolSize,
            'dbConfTimeout': self.callTimeout
        }
        logmsg = '%s: [IDT:GetStatus] [rc:200; Success] [Queue:%s] ' % \
                 (request.method, self.qsize)
        self.log.info(logmsg)
        # except:
        #     stat = {'rc' : 500,
        #             'message': 'Some server error'}
        return web.json_response(stat, status=stat['rc'])