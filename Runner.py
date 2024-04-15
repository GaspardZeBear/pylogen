import re
import os
import time
import datetime
import logging
from datetime import datetime,timedelta
from RequestsManager import *
from Request import *
from QueueSender import *

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
    self.id=self.args.id
    self.pid=os.getpid()
    self.setStartTime()
    self.setStopTime()
    self.stopTimem1=self.stopTime
    self.thru=0
    self.setFullId()
    self.queue=self.parms["queue"]
    self.queueSender=self.parms["queueSender"]
    self.controllerQueue=self.parms["controllerQueue"]
    self.name=self.args.id
    now=datetime.datetime.now()
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
  def setFullId(self,qualifier=0) :
    self.fullId=f'{self.args.id}.{self.childClassName}.{qualifier}'

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
      if "type" in work :
        if work["type"] == "cmd" and work["cmd"]=="stop" :
          logging.info(f'{self.name} getting stop cmd event, exiting')
          break
      elif work is None :
        logging.info(f'{self.name} null event, exiting')
        break
      self.sendWorkersActivityStats(1)
      now=time.time() 
      waitTime=now - work["genTime"]
      logging.debug(f'now {now} event : {work} waited {waitTime}')
      self.controllerQueue.put({'from':'worker','pid':self.id,'msg':'busy'})
      self.loopOnLengths(cut)
      self.controllerQueue.put({'from':'worker','msg':'event','wait':waitTime})
      logging.debug(f'{self.name} loopQueue() processed {waitTime=}')
      self.controllerQueue.put({'from':'worker','pid':self.id,'msg':'idle'})
      self.sendWorkersActivityStats(-1)
    logging.info(f'{self.name} loopQueue() terminated ')
    self.controllerQueue.put({'from':'worker','id':self.id,'pid':self.pid,'msg':'terminated'})

  #----------------------------------------------------------------------
  def sendWorkersActivityStats(self,count) :
    self.queueSender.sendMsgToQueue("activity",{"busyWorkers" : count})

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
    while (datetime.datetime.now() < self.exitTime ) :
      logging.info(f'{self.name} loopDuration() ')
      self.sendWorkersActivityStats(1) 
      self.loopOnLengths(cut)
      self.sendWorkersActivityStats(-1)
      time.sleep(float(self.args.pauseloop))

  #--------------------------------------------------------------------------------------
  def sendError(self,e) :
    self.sendMsgToQueue("error",{"fullId": f'{self.fullId}.{self.requestName}',"error" : f'{e}'})

  #--------------------------------------------------------------------------------------
  def reportTransaction(self,rm,r,step) :
    self.queueSender.sendMsgToQueue("report",{
        "time" : rm.getRequests()[0].getBegin().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "epoch" : rm.getRequests()[0].getBegin().timestamp(),
        "fullId" : f'{self.fullId}.{rm.getName()}',
        "opcount" : self.opCount,
        "nature" : "tra",
        "transactionId" : self.transactionId,
        "thru" : self.thru,
        "rc": rm.getRc(),
        "step" : step,
    })

  #--------------------------------------------------------------------------------------
  def reportRequest(self,rm,r,pStep) :
    thru=self.thru
    opCount=self.opCount
    if self.isTransaction :
      thru=-1
      opCount=0
    self.queueSender.sendMsgToQueue("report",{
        "time" : r.getBegin().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "epoch" : r.getBegin().timestamp(),
        "fullId" : f'{self.fullId}.{rm.getName()}.{r.getName()}',
        "opcount" : opCount,
        "nature" : "req",
        "transactionId" : self.transactionId,
        "thru" : thru,
        "rc": r.getRc(),
        "step" : pStep,
        "delta": r.getDuration()
    })


  #--------------------------------------------------------------------------------------
  def loopOnLengths(self,cut) :
    steps=[x for x in re.split(',',self.args.steps) ]
    cut.resetBeforeSteps()
    for j in range(0,len(steps)) :
      self.opCount += 1
      cut.resetBeforeStep()
      cut.setStep(steps[j])
      cut.genDatas()
      cut.processDatas()
      cut.func()
      rmngr=cut.getRequestsManager()
      delta = rmngr.getDuration()
      now=datetime.datetime.now()
      t=now.strftime("%Y-%m-%d %H:%M:%S.%f")
      te=now.timestamp()
      nowTime=time.time()
      interval=nowTime - self.last
      if (interval > self.opThresh) :
        self.thru = (self.opCount - self.opCountLast) / interval
        self.last=nowTime
        self.opCountLast=self.opCount
      self.setFullId(j)
      if  len(rmngr.getRequests()) > 1 :
        self.transactionId=f'{self.id}.{self.opCount}'
        self.isTransaction=True
        self.reportTransaction(rmngr,None,steps[j])
      else :
        self.isTransaction=False
        self.transactionId=f'None'
      for r in rmngr.getRequests() :
        self.reportRequest(rmngr,r,steps[j])
      time.sleep(float(self.args.pausestep))

