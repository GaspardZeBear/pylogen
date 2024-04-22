import multiprocessing
from multiprocessing import Process,Event,Queue
import logging
import time
import datetime
import logging
import random
from datetime import datetime,timedelta
from OPScheduler import *

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

  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args}')
      count=0
      msg=self.generatorQueue.get()
      logging.info(f'Got go from {msg}')
      for schedule in self.schedules :
        scheduler=OPScheduler(self.args,self.parms,schedule,count)
        scheduler.generate()
        count += scheduler.getCount()
      logging.info(f'{self.name} generator ended generated {count=} events')
      self.controllerQueue.put({"from":"generator","msg":"over","count":count})
    except Exception as e :
      logging.exception(f'{e}',stack_info=True,exc_info=True)
      print(f'OPGenerator {e}')

