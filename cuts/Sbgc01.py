import base64
import datetime
import time
import sys
import re
import hashlib
import logging
import requests
import json
from ClassUnderTest import *
from RequestsManager import *
from Executor import *

class Sbgc01(ClassUnderTest) :

  #-------------------------------------------------------------------
  def __init__(self,args,parms) :
    logging.debug("Sbgc01 starting")
    logging.debug(f'args={args} parms={parms}')
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
    logging.debug("Sbgc01 func() called")
    self.count += 1
    self.runSbgc01Executor(self.requestsManager.newRequest('R0'))
    self.requestsManager.close()
    logging.debug("Sbgc01 func() ending")

  #-------------------------------------------------------------------
  @Executor.exec
  def runSbgc01Executor(self,pSleep=None) :
    logging.debug("Sbgc01 runSbgc01Executor() called")
    #url="http://localhost:8080//dumby/{maxIndex}/{count}/{size}/{sleep}/{deepsleep}"
    url="http://localhost:8080//dumby/256/256/256/100/0"
    #requests.get(self.extra["sbgc"])
    resp=requests.get(url)
    print(resp.status_code)
    logging.debug("Sbgc01 runSbgc01Executor() ending")
