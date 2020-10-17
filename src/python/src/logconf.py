import io
import pathlib
import sys

import yaml
from loguru import logger


class LoguruLogger(object):
    def __init__(self, lpatch=str(pathlib.Path().absolute()) + '/'):
        self.log = logger
        self.log = self._get_logger(lpatch)

    def _get_logger(self, lpatch):
        with self.log.catch(message='Error load config/config_log.yaml', onerror=lambda _: sys.exit(1)):
            with io.open(lpatch + 'config/config_log.yaml', encoding='utf-8') as file:
                _logparms = yaml.load(file, Loader=yaml.FullLoader)
                if _logparms['loguruconf']['handlers'] is not None:
                    for log_parms in _logparms['loguruconf']['handlers']:
                        self.log.add(**log_parms)
        logger.info('logger configuration imported' + str(_logparms))
        return logger
