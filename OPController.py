import multiprocessing
import os
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
    self.queue=self.parms["queue"]
    self.jobsQueue=self.parms["jobsQueue"]
    self.controllerQueue=self.parms["controllerQueue"]
    self.generatorQueue=self.parms["generatorQueue"]
    self.controllerDelay=float(self.args.controllerDelay)
    self.trigger=int(self.args.trigger)
    self.decreaseArgs=int(self.args.decrease)
    self.workersStartedSum=0
    self.workersTerminatedSum=0
    self.workersRunningCount = 0
    self.eventGenerated=0
    self.eventGeneratedSignaled=0
    self.eventProcessed=0
    self.busyWorkersSum=0
    self.idleWorkersSum=0
    self.busyWorkersCount=0
    self.waitTime=-1
    self.decrease=0
    self.generatorOver=False

  #-----------------------------------------------------------------------------------------------
  def launchPreforkWorkers(self):
    for i in range(0,int(self.args.prefork)) :
      logging.info(f'{self.name} prefork worker {i}')
      CutLauncher(self.args,self.parms)
    # waiting all preforked CUTs ready
    readyCount=0 
    while readyCount < int(self.args.prefork) :
      logging.debug(f'Controller waiting for ready, current {readyCount=}')
      msg=self.controllerQueue.get(True,self.controllerDelay)
      if msg["from"] == "worker" and msg["msg"] == "ready" :
        readyCount += 1
        self.workersStartedSum += 1
        self.workersRunningCount += 1
        #self.sendWorkersActivityStats()
      else : 
        logging.error(f'Controller discarding {msg} in controllerQueue')

    logging.warning(f'Controller got all preforked workers {readyCount=}')

  #-----------------------------------------------------------------------------------------------
  def processControllerQueueMsg(self,msg):
    if msg["from"] == "generator" and msg["msg"] == "over" :
      self.generatorOver=True
      pendingEvents = self.eventGenerated - self.eventProcessed
      logging.debug(f'Generator is over,  {self.eventGenerated=} {self.eventProcessed=} {pendingEvents=}')
    elif msg["from"] == "generator" and msg["msg"] == "event" :
      self.eventGenerated += 1
    elif msg["from"] == "worker" and msg["msg"] == "event" :
      self.eventProcessed += 1
      self.waitTime = msg["wait"]
    elif msg["from"] == "worker" and msg["msg"] == "ready" :
      self.workersStartedSum += 1
      self.workersRunningCount += 1
      #self.sendWorkersActivityStats()
    elif msg["from"] == "worker" and msg["msg"] == "terminated" :
      self.workersTerminatedSum += 1
      self.workersRunningCount -= 1
      #self.sendWorkersActivityStats()
    elif msg["from"] == "worker" and msg["msg"] == "busy" :
      self.busyWorkersSum += 1
      self.busyWorkersCount += 1
      #self.sendWorkersActivityStats()
    elif msg["from"] == "worker" and msg["msg"] == "idle" :
      self.idleWorkersSum += 1
      self.busyWorkersCount -= 1
      #self.sendWorkersActivityStats()
    else :
      logging.debug(f'Controller ignoring {msg} in controllerQueue')

  #-----------------------------------------------------------------------------------------------
  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args} {self.pid=}')
      logging.warning(f'Controller launching prefork workers')
      self.launchPreforkWorkers()
      logging.warning(f'Controller giving go to generator')
      self.generatorQueue.put({"from":"controller","msg":"go"})
      while not self.generatorOver or ( self.eventGenerated > self.eventProcessed)  :
        try:
          loops = 0
          while loops < self.trigger  :
            loops += 1
            msg=self.controllerQueue.get(True,self.controllerDelay)
            logging.debug(f'Controller got {msg} in controllerQueue')
            self.processControllerQueueMsg(msg)
        except Empty:
          logging.debug(f'Controller got nothing in controllerQueue')
          pass
        qsize= self.jobsQueue.qsize()
        children=multiprocessing.active_children()
        if (self.eventGenerated % 10 == 0) and (self.eventGenerated > self.eventGeneratedSignaled ):
          self.eventGeneratedSignaled = self.eventGenerated
          logging.info(f'{self.name} {qsize=} children {len(children)} {self.eventGenerated=} {self.eventProcessed=} last {self.waitTime=} {self.workersRunningCount=} {self.busyWorkersCount=}')
        logging.debug(f'{self.name} {qsize=} children {len(children)} {self.eventGenerated=} {self.eventProcessed=} last {self.waitTime=} {self.workersRunningCount=} {self.busyWorkersCount=}')
        if self.jobsQueue.qsize() > self.trigger :
          delay=self.controllerDelay/10
          self.decrease=0
          logging.info(f'jobQueueSize > trigger{self.name} : starting Worker')
          CutLauncher(self.args,self.parms)
        else :
          delay=self.controllerDelay
          self.decrease += 1
          if self.decrease > self.decreaseArgs :
            logging.info(f'Sending work=None to jobsQueue')
            self.jobsQueue.put(None)
            self.decrease=0
      logging.warning(f'Controller exited from main loop {self.generatorOver=}  {self.eventGenerated=} {self.eventProcessed=}')
      children=multiprocessing.active_children()
      childrenCount=len(children)
      for child in children :
        logging.warning(f'Remaining worker  {child=} {childrenCount=}')
      for i in range(0,childrenCount) : 
        logging.info(f'Sending work=None number {i} to jobsQueue')
        self.jobsQueue.put(None)
     
      # trying to force read of jobsQueue as workers don't read it ! 
      # Strange ! Should not have to do that
      for i in range(0,childrenCount) :
        try :
          #msg=self.jobsQueue.get(True,self.controllerDelay)
          msg=self.jobsQueue.get(True,0.01)
          logging.debug(f'jobsQueue check {i=} Controller got {msg} in controllerQueue')
        except Empty:
          logging.debug(f'jobsQueue check {i=} Controller got nothing in controllerQueue')
          pass

    except Exception as e :
      logging.exception(f'{e}',stack_info=True,exc_info=True)


  #----------------------------------------------------------------------
  def sendWorkersActivityStats(self) :
    activity={
        "type" : "activity",
        "from" : "controller",
        "id" : self.pid,
        "runningWorkers" : self.workersRunningCount,
        "busyWorkers" : self.busyWorkersCount,
    }
    self.queue.putQueue(activity)

