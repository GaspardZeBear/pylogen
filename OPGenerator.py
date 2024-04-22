import multiprocessing
from multiprocessing import Process,Event,Queue
import logging
import time
import datetime
import logging
import random
from datetime import datetime,timedelta

# custom process class
class OPGenerator(Process):
  def __init__(self,args,parms) :
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.name="Generator"
    self.args=args
    self.parms=parms
    self.queue=self.parms["queue"]
    self.jobsQueue=self.parms["jobsQueue"]
    self.controllerQueue=self.parms["controllerQueue"]
    self.generatorQueue=self.parms["generatorQueue"]
    self.generatorDelay=float(self.args.generatorDelay)
    self.schedules=self.args.schedule.split(',')

  def getSleepDuration(self,begin,end,now,thruBegin,thruEnd) :
    thru=(now-begin)*(thruEnd-thruBegin)/(end-begin) + thruBegin
    logging.debug(f'{begin=} {end=} {now=} {thruBegin=} {thruEnd=} {thru=}')
    return(1/thru)

  def getBurstCycle(self,burstMax) :
    burstArgs = int(self.args.burst)
    if burstArgs == 0 :
      burstCycle=random.randint(1,burstMax)
    else :
      burstCycle=random.randint(1,burstArgs)
    #return(1)
    logging.debug(f'Next burst will contains {burstCycle=} events')
    return(burstCycle)

    
  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args}')
      count=0
      msg=self.generatorQueue.get()
      logging.info(f'Got go from {msg}')
      for schedule in self.schedules :
        logging.info(f' {self.name} {schedule}')
        duration,thru0=schedule.split('@')
        if '-' in thru0 :
          tb,te=thru0.split('-')
          thruBegin=float(tb)
          thruEnd=float(te)
        else : 
          thruBegin=float(thru0)
          thruEnd=float(thru0)
        burstMax=int((thruEnd- thruBegin)/2)

        logging.info(f' {self.name} {duration=} {thruBegin=} {thruEnd=}')
        #now=datetime.now()
        now = time.time()
        begin = now
        end=now + int(duration)
        burstCycle=self.getBurstCycle(burstMax)
        burstSkip = 0
        while now < end :
          sleepDuration=self.getSleepDuration(begin,end,now,thruBegin,thruEnd)
          #time.sleep(1/float(thru))
          time.sleep(sleepDuration)
          if burstSkip == 0 :
            burstCount = 0
            while burstCycle > 0 :
              count += 1
              logging.debug(f'{self.name} {now=} {end=}  generates event {count=} {burstCycle=}')
              self.jobsQueue.put({"type":"event","genTime":now})
              self.controllerQueue.put({"from":"generator","msg":"event","count":count})
              burstCycle -= 1
              burstCount += 1
              if burstCount > 1 :
                burstSkip += 1
            burstCycle=self.getBurstCycle(burstMax)
          else : 
            logging.debug(f'{self.name} {now=} {end=}  skipping burst event {count=} {burstSkip=}')
            burstSkip -= 1
          now=time.time()
          if (count % 100) == 0 :
            logging.info(f'{self.name} generated {count=} events')
      logging.info(f'{self.name} generator ended generated {count=} events')
      self.controllerQueue.put({"from":"generator","msg":"over","count":count})
    except Exception as e :
      logging.exception(f'{e}',stack_info=True,exc_info=True)
      print(f'OPGenerator {e}')

