import re
import os
import time
import datetime
import logging
from datetime import datetime,timedelta
from RequestsManager import *
from Request import *

#----------------------------------------------
class Runner() :

  #--------------------------------------------------------------------------------------
  def __init__(self,args,parms) :
    self.args=args
    self.parms=parms
    self.pNum=parms["pNum"]
    self.childClassName=parms["childClassName"]
    self.stepName='default'
    self.requestName='default'
    self.rc=-1
    self.requestRc=-1
    self.opCount=0
    self.opCountLast=0
    self.opThresh=100
    self.opThresh=int(self.args.summary)
    self.last=time.time()
    #self.setTransaction(False)
    self.id=os.getpid()
    self.setStartTime()
    self.setStopTime()
    self.stopTimem1=self.stopTime
    self.thru=0
    self.setFullId()
    self.queue=self.parms["queue"]
    self.controllerQueue=self.parms["controllerQueue"]
    self.name=self.args.id
    now=datetime.now()
    if self.args.openedmodel :
      logging.info(f"Opened model")
      self.loopMethod=self.loopQueue
    else : 
      if int(self.args.duration) > 0 :
        logging.info(f"Closed model with duration {self.args.duration}")
        self.loopMethod=self.loopDuration
        self.exitTime=now + timedelta(seconds=int(self.args.duration))
      else :
        logging.info(f"Closed model with loops {self.args.loops}")
        self.loopMethod=self.loopLoop

  #--------------------------------------------------------------------------------------
  def setTransaction(self,transaction) :
    self.isTransaction=transaction
    if transaction :
      self.transactionId=f'{self.id}.{self.opCount}'
    else :
      self.transactionId=f'None'
    self.setFullId('')
      
      
  #--------------------------------------------------------------------------------------
  def setFullId(self,qualifier='') :
    if len(qualifier) == 0 :
      self.fullId=f'{self.args.id}-{self.pNum}.{self.childClassName}'
    else :
      self.fullId=f'{self.args.id}-{self.pNum}.{self.childClassName}.{qualifier}'

  #--------------------------------------------------------------------------------------
  def setRequestName(self,name) :
    self.requestName=name

  #--------------------------------------------------------------------------------------
  def setStartTime(self) :
    self.startTime=time.time()

  #--------------------------------------------------------------------------------------
  def setStopTime(self) :
    self.stopTime=time.time()

  #--------------------------------------------------------------------------------------
  def loop(self,cut) :
    try :
      logging.debug(f'loop() called, will trigger self.loopMethod {self.loopMethod}')
      self.loopMethod(cut)
    except KeyboardInterrupt:
      print("Caught KeyboardInterrupt, terminating loop")
    except Exception as e :
      print(f'loop stopped {e}')

  #--------------------------------------------------------------------------------------
  def loopQueue(self,cut) :
    logging.info(f'{self.name} loopQueue() starting ')
    self.controllerQueue.put({'from':'worker','pid':self.id,'msg':'ready'})
    while True :
      logging.debug(f'{self.name} loopQueue() waiting for event in jobQueue')
      work=self.parms["jobsQueue"].get()
      logging.info(f'{work=}')
      if work is None :
        logging.info(f'{self.name} null event, exiting')
        break
      self.sendWorkersActivityStats(1)
      now=time.time() 
      waitTime=now - work["genTime"]
      logging.debug(f'now {now} event : {work} waited {waitTime}')
      #print(f'{self.name} loopQueue() will process {waitTime=}')
      self.controllerQueue.put({'from':'worker','pid':self.id,'msg':'busy'})
      self.loopOnLengths(cut)
      self.controllerQueue.put({'from':'worker','msg':'event','wait':waitTime})
      logging.debug(f'{self.name} loopQueue() processed {waitTime=}')
      self.controllerQueue.put({'from':'worker','pid':self.id,'msg':'idle'})
      self.sendWorkersActivityStats(-1)
    logging.info(f'{self.name} loopQueue() terminated ')
    self.controllerQueue.put({'from':'worker','pid':self.id,'msg':'terminated'})

  #----------------------------------------------------------------------
  def sendWorkersActivityStats(self,count) :
    activity={
        "type" : "activity",
        "from" : "worker",
        "id" : self.id,
        "busyWorkers" : count
    }
    self.queue.putQueue(activity)

  #--------------------------------------------------------------------------------------
  def loopLoop(self,cut) :
    for i in range(0,int(self.args.loops)) :
      self.sendWorkersActivityStats(1) 
      logging.info(f'{self.name} loopLoop() {i}')
      self.loopOnLengths(cut)
      self.sendWorkersActivityStats(-1) 
      time.sleep(float(self.args.pauseloop))

  #--------------------------------------------------------------------------------------
  def loopDuration(self,cut) :
    while (datetime.now() < self.exitTime ) :
      logging.info(f'{self.name} loopDuration() ')
      self.sendWorkersActivityStats(1) 
      self.loopOnLengths(cut)
      self.sendWorkersActivityStats(-1)
      time.sleep(float(self.args.pauseloop))

  #--------------------------------------------------------------------------------------
  def sendError(self,e) :
    now=datetime.now()
    t=now.strftime("%Y-%m-%d %H:%M:%S.%f")
    te=now.timestamp()
    err={
      "type": "error",
      "error" : {
         "time" : t,
         "epoch" : te,
         "fullId": f'{self.fullId}.{self.requestName}',
         "error" : f'{e}'
      }
    }
    self.queue.putQueue(err)
      

  #--------------------------------------------------------------------------------------
  def reportTransaction(self,rm,r,length) :
    t=rm.getRequests()[0].getBegin().strftime("%Y-%m-%d %H:%M:%S.%f")
    te=rm.getRequests()[0].getBegin().timestamp()
    report={
       "type" : "report",
        "time" : t,
        "epoch" : te,
        "pid" : self.id,
        "fullId" : f'{self.fullId}.{rm.getName()}',
        "opcount" : self.opCount,
        "nature" : "tra",
        "transactionId" : self.transactionId,
        "thru" : self.thru,
        "rc": rm.getRc(),
        "length" : length,
        "delta": rm.getDuration()
    }
    self.queue.putQueue(report)

  #--------------------------------------------------------------------------------------
  def reportRequest(self,rm,r,pLength) :
    t=r.getBegin().strftime("%Y-%m-%d %H:%M:%S.%f")
    te=r.getBegin().timestamp()
    thru=self.thru
    opCount=self.opCount
    length=pLength
    if self.isTransaction :
      thru=-1
      #length=-1
      opCount=0
    report={
       "type" : "report",
        "time" : t,
        "epoch" : te,
        "pid" : self.id,
        "fullId" : f'{self.fullId}.{rm.getName()}.{r.getName()}',
        "opcount" : opCount,
        "nature" : "req",
        "transactionId" : self.transactionId,
        "thru" : thru,
        "rc": r.getRc(),
        "length" : length,
        "delta": r.getDuration()
    }
    self.queue.putQueue(report)

  #--------------------------------------------------------------------------------------
  def loopOnLengths(self,cut) :
    #logging.info(f'{self.name} event called')
    lengths=[int(x) for x in re.split(',',self.args.lengths) ]
    for j in range(0,len(lengths)) :
      #logging.info(f'{self.name} loop {j}')
      self.opCount += 1
      cut.reset()
      cut.genDatas(lengths[j])
      cut.processDatas()
      cut.func()
      rmngr=cut.getRequestsManager()
      delta = rmngr.getDuration()
      now=datetime.now()
      t=now.strftime("%Y-%m-%d %H:%M:%S.%f")
      te=now.timestamp()
      nowTime=time.time()
      interval=nowTime - self.last
      if (interval > self.opThresh) :
        self.thru = (self.opCount - self.opCountLast) / interval
        self.last=nowTime
        self.opCountLast=self.opCount
      self.fullId=f'{self.args.id}-{self.pNum}.{self.childClassName}'
      if  len(rmngr.getRequests()) > 1 :
        self.transactionId=f'{self.id}.{self.opCount}'
        self.isTransaction=True
        self.reportTransaction(rmngr,None,lengths[j])
      else :
        self.isTransaction=False
        self.transactionId=f'None'
      for r in rmngr.getRequests() :
        self.reportRequest(rmngr,r,lengths[j])
      time.sleep(float(self.args.pauselen))

