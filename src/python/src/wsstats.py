# ************* Import
import time

from .logconf import LoguruLogger


# ************* Status  Check
class WSStatistic(LoguruLogger):
    def __init__(self, lpatch):
        super().__init__(lpatch)
        self.StatstartStatTime = time.monotonic()
        self.StatlastSuccess = time.monotonic()
        self.StatlastError = time.monotonic()
        self.log.info('Health check initialized')

    def calc_stat(self, rc):
        if rc == 200:
            self.StatlastSuccess = time.monotonic()
        else:
            self.StatlastError = time.monotonic()
