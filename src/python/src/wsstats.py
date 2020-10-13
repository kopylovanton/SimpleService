# ************* Import
import time

from .logconf import LoguruLogger


# ************* Status  Check
class WSStatistic(LoguruLogger):
    def __init__(self, lpatch):
        super().__init__(lpatch)
        self.StatstartStatTime = time.time()
        self.StatlastSuccess = time.time()
        self.StatlastError = time.time()
        self.log.info('Health check initialized')

    def calc_stat(self, rc):
        if rc == 200:
            self.StatlastSuccess = time.time()
        else:
            self.StatlastError = time.time()
