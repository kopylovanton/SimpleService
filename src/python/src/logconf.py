import io
import pathlib
import sys

import yaml
from loguru import logger


class LoguruLogger(object):
    def __init__(self, lpatch=str(pathlib.Path().absolute()) + '/'):
        self.log = self._get_logger(lpatch)

    @staticmethod
    def _get_logger(lpatch):
        with logger.catch(onerror=lambda _: sys.exit(1)):
            with io.open(lpatch + 'config/config_log.yaml', encoding='utf-8') as file:
                _logparms = yaml.load(file, Loader=yaml.FullLoader)
        if _logparms.get('loguruconf', []).get('handlers', False):
            logger.configure(**_logparms['loguruconf'])
        if _logparms.get('stdout', False):
            logger.add(sys.stdout)
        logger.info('logger configuration imported' + str(_logparms))
        return logger
