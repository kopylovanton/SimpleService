# ************* Import
import time
# ************* Status  Check
class WSStatistic(object):
    def __init__(self,depthMin=5):
        self.__startTime = time.time()
        self.__getItems={}
        self.__errorsCount = {}
        self.__depthMin=depthMin
    def __trimItem(self,ditems):
        filtTime = (time.time() - self.__startTime) // 60 - self.__depthMin
        ditems = {k: v for k, v in ditems.items() if k>=filtTime}
        return ditems
    def putGetItem(self,durationSec):
        """ add durations stat for request"""
        #start_time=time.time()
        upTimeMin = (time.time() - self.__startTime) // 60
        if len(self.__getItems)>1000:
            self.__getItems=self.__trimItem(self.__getItems)
        self.__getItems[upTimeMin]=self.__getItems.get(upTimeMin, {'duration':0,'count':0})
        self.__getItems[upTimeMin]['duration'] += round(durationSec,4)
        self.__getItems[upTimeMin]['count'] +=  1
        #dtime = round(time.time() - start_time, 4)
        #log.info("Put statistics processed in --- %s seconds ---" % (dtime))
    def putErrItem(self):
        """ add error count"""
        upTimeMin = (time.time() - self.__startTime) // 60
        if len(self.__errorsCount) > 1000:
            self.__errorsCount=self.__trimItem(self.__errorsCount)
        self.__errorsCount[upTimeMin] = self.__errorsCount.get(upTimeMin, 0) + 1
    def getStat(self):
        """calculate statistics"""

        self.__getItems = self.__trimItem(self.__getItems)
        self.__errorsCount = self.__trimItem(self.__errorsCount)
        stat={  'getCount':0,
                'meanGetDuration':0,
                'errorsCount':0,
                'up_time_min': round((time.time() - self.__startTime) / 60,1)
              }
        for i in self.__getItems:
            stat['getCount'] += self.__getItems[i]['count']
            stat['meanGetDuration'] += self.__getItems[i]['duration']
        if stat['getCount']>0:
            stat['meanGetDuration']=round(stat['meanGetDuration']/stat['getCount'],4)
        for i in self.__errorsCount:
            stat['getCount'] += self.__errorsCount[i]
        return stat