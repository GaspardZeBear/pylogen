import base64
import datetime
import time
import sys
import re
import hashlib
import logging
import json
from ClassUnderTest import *
from RequestsManager import *
from Executor import *

class Dummy(ClassUnderTest) :

  #-------------------------------------------------------------------
  def __init__(self,args,parms) :
    logging.info("starting")
    logging.info(f'args={args} parms={parms}')
    super().__init__(args,parms)
    self.parms=parms
    self.args=args
    self.extra=json.loads(self.args.extra)
    self.sleep=1
    if "sleep" in self.extra :
      self.sleep = float(self.extra["sleep"])
    self.count=0
    #self.requestsManager=None

  #-------------------------------------------------------------------
  #def getRequestsManager(self) :
  #  return(self.requestsManager)

  #-------------------------------------------------------------------
  def processDatas(self) :
    pass

  #-------------------------------------------------------------------
  def func(self) :
    self.count += 1
    #self.requestsManager=RequestsManager("KMSDUMMY")
    if "transaction" in self.extra :
      self.runDummyTransactionExecutor()
    else :
      if "error" in self.extra :
        if (self.count % self.extra["error"]) == 0 :
          self.runDummyExecutorError()
        else :
          self.runDummyExecutor(self.requestsManager.newRequest('R0'))
      else :
        self.runDummyExecutor(self.requestsManager.newRequest('R0'))
    self.requestsManager.close()

  #-------------------------------------------------------------------
  @Executor.exec
  def runDummyExecutor(self,pSleep=None) :
    sleep=self.sleep
    if pSleep is not None :
      sleep=pSleep      
    time.sleep(float(sleep))

  #-------------------------------------------------------------------
  def runDummyExecutorError(self):
    self.runDummyExecutor(self.requestsManager.newRequest("R-ERROR"),'X')

  #-------------------------------------------------------------------
  def runDummyTransactionExecutor(self):
    for i in range(0,3) :
      self.runDummyExecutor(self.requestsManager.newRequest(f"R{i}-EXEC"))
