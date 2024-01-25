import multiprocessing
from multiprocessing import Process,Event,Queue
import logging
import time
from OPWorker import *

# custom process class
class OPController(Process):
  def __init__(self,args) :
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.name="Controller"
    self.args=args
    self.jobsQueue=self.args.jobsQueue
    self.controllerDelay=float(self.args.controllerDelay)
    self.trigger=int(self.args.trigger)
    self.decrease=int(self.args.decrease)

  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args}')
      decrease=0
      while True :
        qsize= self.jobsQueue.qsize()
        children=multiprocessing.active_children()
        logging.info(f'{self.name} {qsize=} children {len(children)}')
        if self.jobsQueue.qsize() > self.trigger :
          delay=self.controllerDelay/10
          decrease=0
          logging.info(f'{self.name} starting Worker')
          worker=OPWorker(self.args)
          worker.daemon=True
          worker.start()
        else :
          delay=self.controllerDelay
          decrease += 1
          if decrease > self.decrease :
            self.jobsQueue.put(None)
            decrease=0
        #logging.info(f'{self.name} sleeping')
        #time.sleep(self.controllerDelay)
        time.sleep(delay)
    except Exception as e :
      print(f'{e}')
