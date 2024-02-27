import multiprocessing
from multiprocessing import Process,Event,Queue
import logging
import time
import datetime
import logging
from datetime import datetime,timedelta

# custom process class
class OPGenerator(Process):
  def __init__(self,args,parms) :
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.name="Generator"
    self.args=args
    self.jobsQueue=self.parms.jobsQueue
    self.controllerQueue=self.parms["controllerQueue"]
    self.generatorQueue=self.parms["generatorQueue"]
    self.generatorDelay=float(self.args.generatorDelay)
    self.schedules=self.args.schedule.split(',')


  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args}')
      count=0
      msg=self.generatorQueue.get()
      logging.info(f'Got go from {msg}')
      for schedule in self.schedules :
        logging.info(f' {self.name} {schedule}')
        duration,thru=schedule.split('@')
        logging.info(f' {self.name} {duration=} {thru=}')
        #now=datetime.now()
        now = time.time()
        end=now + int(duration)
        while now < end :
          time.sleep(1/float(thru))
          logging.debug(f'{self.name} {now=} {end=}  generates event')
          self.jobsQueue.put({"genTime":now})
          count += 1
          self.controllerQueue.put({"from":"generator","msg":"event","count":count})
          now=time.time()
          if (count % 100) == 0 :
            logging.info(f'{self.name} generated {count=} events')
      logging.info(f'{self.name} generator ended generated {count=} events')
      self.controllerQueue.put({"from":"generator","msg":"over","count":count})
    except Exception as e :
      print(f'OPGenerator {e}')

