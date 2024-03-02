import multiprocessing
from multiprocessing import Process,Event,Queue
from queue import Empty
import logging
import time
from OPWorker import *
from CutLauncher import *

# custom process class
class OPController(Process):
  def __init__(self,args,parms) :
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.name="Controller"
    self.args=args
    self.parms=parms
    self.jobsQueue=self.parms["jobsQueue"]
    self.controllerQueue=self.parms["controllerQueue"]
    self.generatorQueue=self.parms["generatorQueue"]
    self.controllerDelay=float(self.args.controllerDelay)
    self.trigger=int(self.args.trigger)
    self.decrease=int(self.args.decrease)

  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args}')
      for i in range(0,int(self.args.prefork)) :
        logging.info(f'{self.name} prefork worker {i}')
        CutLauncher(self.args,self.parms)
      decrease=0
      eventGenerated=0
      eventGeneratedSignaled=0
      eventProcessed=0
      waitTime=-1
      generatorOver=False
      self.generatorQueue.put({"from":"controller","msg":"go"})
      #while True :
      while not generatorOver or ( eventGenerated > eventProcessed)  :
        try:
          loops = 0
          #while True :
          while loops < self.trigger  :
            loops += 1
            msg=self.controllerQueue.get(False)
            logging.debug(f'Controller got {msg} in controllerQueue')
            if msg["from"] == "generator" and msg["msg"] == "over" :
              generatorOver=True
            elif msg["from"] == "generator" and msg["msg"] == "event" :
              eventGenerated += 1
            elif msg["from"] == "worker" and msg["msg"] == "event" :
              eventProcessed += 1
              waitTime = msg["wait"]
            else :
              logging.debug(f'Controller ignoring {msg} in controllerQueue')
        except Empty:
          logging.debug(f'Controller got nothing in controllerQueue')
        qsize= self.jobsQueue.qsize()
        children=multiprocessing.active_children()
        #logging.info(f'{self.name} {qsize=} children {len(children)} eventGenerated {eventGenerated} eventProcessed {eventProcessed} last waitTime {waitTime}')
        if (eventGenerated % 10 == 0) and (eventGenerated > eventGeneratedSignaled ):
          eventGeneratedSignaled = eventGenerated
          print(f'{self.name} {qsize=} children {len(children)} eventGenerated {eventGenerated} eventProcessed {eventProcessed} last waitTime {waitTime}')
        if self.jobsQueue.qsize() > self.trigger :
          delay=self.controllerDelay/10
          decrease=0
          logging.info(f'jobQueueSize > trigger{self.name} : starting Worker')
          #worker=OPWorker(self.args)
          #worker.daemon=True
          #worker.start()
          CutLauncher(self.args,self.parms)
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
