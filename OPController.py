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
      workersStartedSum=0
      workersStoppedSum=0
      workersRunningCount = workersStartedSum - workersStoppedSum
      for i in range(0,int(self.args.prefork)) :
        logging.info(f'{self.name} prefork worker {i}')
        workersStartedSum += 1
        workersRunningCount = workersStartedSum - workersStoppedSum
        CutLauncher(self.args,self.parms)

      # waiting all preforked CUTs ready
      readyCount=0 
      while readyCount < int(self.args.prefork) :
        logging.warning(f'Controller waiting for ready, current {readyCount=}')
        msg=self.controllerQueue.get(True,self.controllerDelay)
        if msg["from"] == "worker" and msg["msg"] == "ready" :
          readyCount += 1
        else : 
          logging.warning(f'Controller discarding {msg} in controllerQueue')

      logging.warning(f'Controller got all preforked workers {readyCount=}')
      decrease=0
      eventGenerated=0
      eventGeneratedSignaled=0
      eventProcessed=0
      busyWorkersSum=0
      idleWorkersSum=0
      busyWorkersCount=0
      waitTime=-1
      generatorOver=False
      logging.warning(f'Controller giving go to generator')
      self.generatorQueue.put({"from":"controller","msg":"go"})
      #while True :
      while not generatorOver or ( eventGenerated > eventProcessed)  :
        try:
          loops = 0
          #while True :
          while loops < self.trigger  :
            loops += 1
            # msg=self.controllerQueue.get(False)
            msg=self.controllerQueue.get(True,self.controllerDelay)
            logging.debug(f'Controller got {msg} in controllerQueue')
            if msg["from"] == "generator" and msg["msg"] == "over" :
              generatorOver=True
              pendingEvents = eventGenerated - eventProcessed
              logging.debug(f'Generator is over,  {eventGenerated=} {eventProcessed=} {pendingEvents=}')
            elif msg["from"] == "generator" and msg["msg"] == "event" :
              eventGenerated += 1
            elif msg["from"] == "worker" and msg["msg"] == "event" :
              eventProcessed += 1
              waitTime = msg["wait"]
            elif msg["from"] == "worker" and msg["msg"] == "busy" :
              busyWorkersSum += 1
              busyWorkersCount += 1
            elif msg["from"] == "worker" and msg["msg"] == "idle" :
              idleWorkersSum += 1
              busyWorkersCount -= 1
            else :
              logging.debug(f'Controller ignoring {msg} in controllerQueue')
        except Empty:
          logging.debug(f'Controller got nothing in controllerQueue')
          pass
        qsize= self.jobsQueue.qsize()
        children=multiprocessing.active_children()
        #logging.info(f'{self.name} {qsize=} children {len(children)} eventGenerated {eventGenerated} eventProcessed {eventProcessed} last waitTime {waitTime}')
        if (eventGenerated % 10 == 0) and (eventGenerated > eventGeneratedSignaled ):
          eventGeneratedSignaled = eventGenerated
          #print(f'{self.name} {qsize=} children {len(children)} eventGenerated {eventGenerated} eventProcessed {eventProcessed} last waitTime {waitTime}')
          logging.info(f'{self.name} {qsize=} children {len(children)} {eventGenerated=} {eventProcessed=} last {waitTime=} {workersRunningCount=} {busyWorkersCount=}')
        logging.debug(f'{self.name} {qsize=} children {len(children)} {eventGenerated=} {eventProcessed=} last {waitTime=} {workersRunningCount=} {busyWorkersCount=}')
        if self.jobsQueue.qsize() > self.trigger :
          delay=self.controllerDelay/10
          decrease=0
          logging.info(f'jobQueueSize > trigger{self.name} : starting Worker')
          #worker=OPWorker(self.args)
          #worker.daemon=True
          #worker.start()
          CutLauncher(self.args,self.parms)
          workersStartedSum += 1
          workersRunningCount = workersStartedSum - workersStoppedSum
        else :
          delay=self.controllerDelay
          decrease += 1
          if decrease > self.decrease :
            workersStoppedSum += 1
            workersRunningCount = workersStartedSum - workersStoppedSum
            self.jobsQueue.put(None)
            decrease=0
        #logging.info(f'{self.name} sleeping for {delay}')
        #time.sleep(self.controllerDelay)
        #time.sleep(delay)
    except Exception as e :
      print(f'{e}')
