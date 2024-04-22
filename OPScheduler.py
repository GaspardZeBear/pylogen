import multiprocessing
from multiprocessing import Process,Event,Queue
import logging
import time
import datetime
import logging
import random
from datetime import datetime,timedelta


#---------------------------------------------------------------------------------------------------------------
class OPScheduler() :

  def __init__(self,args,parms,schedule,countAtStart) :
    logging.info(f'{schedule}')
    self.args=args
    self.parms=parms
    self.queue=self.parms["queue"]
    self.jobsQueue=self.parms["jobsQueue"]
    self.controllerQueue=self.parms["controllerQueue"]
    self.generatorQueue=self.parms["generatorQueue"]
    #self.generatorDelay=float(self.args.generatorDelay)
    self.duration,self.thru0=schedule.split('@')
    if '-' in self.thru0 :
      tb,te=self.thru0.split('-')
      self.thruBegin=float(tb)
      self.thruEnd=float(te)
    else :
      self.thruBegin=float(self.thru0)
      self.thruEnd=float(self.thru0)
    self.eventsToGenerate=int(int(self.duration)*(self.thruEnd+self.thruBegin)/2)
    self.burstMax=int(abs(self.thruEnd- self.thruBegin)/2)
    self.now = time.time()
    self.begin = self.now
    self.end=self.now + int(self.duration)
    self.countAtStart=0
    self.count=0

    logging.info(f'{self.duration=} {self.thruBegin=} {self.thruEnd=} {self.eventsToGenerate=}')
    #now=datetime.now()

  #---------------------------------------------------------------------------------------------------------------
  def getSleepDuration(self,now) :
    thru=(now-self.begin)*(self.thruEnd-self.thruBegin)/(self.end-self.begin) + self.thruBegin
    logging.debug(f'{self.begin=} {self.end=} {now=} {self.thruBegin=} {self.thruEnd=} {thru=}')
    return(1/thru)

  #---------------------------------------------------------------------------------------------------------------
  def getCount(self) :
    return(self.count)

  #---------------------------------------------------------------------------------------------------------------
  def getBurstCycle(self) :
    if self.args.burst.startswith('f') :
      burstCycle = int(self.args.burst[1:])
    else :
      burstArgs = int(self.args.burst)
      if burstArgs == 0 :
        burstCycle=random.randint(1,self.burstMax)
      else :
        burstCycle=random.randint(1,burstArgs)
    #return(1)
    logging.debug(f'Next burst will contains {burstCycle=} events')
    return(burstCycle)

  #---------------------------------------------------------------------------------------------------------------
  def generate(self) :
    burstCycle=self.getBurstCycle()
    burstSkip = 0
    self.now=time.time()
    while self.now < self.end :
      sleepDuration=self.getSleepDuration(self.now)
      #time.sleep(1/float(thru))
      time.sleep(sleepDuration)
      if burstSkip == 0 :
        burstCount = 0
        while burstCycle > 0 :
          if self.count >= self.eventsToGenerate :
            logging.debug(f'Reached {self.eventsToGenerate=} limit, break')
            break
          self.count += 1
          logging.debug(f'{self.now=} {self.end=}  generates event {self.count=} {burstCycle=}')
          self.jobsQueue.put({"type":"event","genTime":self.now})
          self.controllerQueue.put({"from":"generator","msg":"event","count":self.countAtStart + self.count})
          burstCycle -= 1
          burstCount += 1
          if burstCount > 1 :
            burstSkip += 1
        burstCycle=self.getBurstCycle()
      else :
        logging.debug(f'{self.now=} {self.end=}  skipping burst event {self.count=} {burstSkip=}')
        burstSkip -= 1
      self.now=time.time()
      if (self.count % 100) == 0 :
        logging.info(f'generated {self.count=} events')

    while self.count < self.eventsToGenerate :
      self.count += 1
      logging.debug(f'Missing event generated {self.count=} {self.eventsToGenerate=}')
      self.jobsQueue.put({"type":"event","genTime":self.now})
      self.controllerQueue.put({"from":"generator","msg":"event","count":self.countAtStart + self.count})
