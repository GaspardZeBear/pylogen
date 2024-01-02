import datetime
from datetime import *
import time
import logging

#------------------------------------------------------------------------
class Request() :

  def __init__(self,name) :
    self.name=name
    self.begin=None
    self.beginTime=None
    self.end=None
    self.endTime=None
    self.duration=0
    self.error=None
    self.rc=-1
    logging.warning(f" request {self.name} created")

  #------------------------------------------------------------------------
  def launch(self) :
    self.begin=datetime.now()
    self.beginTime=time.time()

  #------------------------------------------------------------------------
  def stop(self) :
    self.endTime=time.time()
    self.end=datetime.now()
    self.duration=self.endTime - self.beginTime

  #------------------------------------------------------------------------
  def getRc(self) :
    return(self.rc)

  #------------------------------------------------------------------------
  def getBegin(self) :
    return(self.begin)

  #------------------------------------------------------------------------
  def getEnd(self) :
    return(self.end)

  #------------------------------------------------------------------------
  def setRc(self,rc) :
    self.rc=rc

  #------------------------------------------------------------------------
  def setError(self,error) :
    self.error=error

  #------------------------------------------------------------------------
  def getError(self) :
    return(self.error)

  #------------------------------------------------------------------------
  def getName(self) :
    return(self.name)

  #------------------------------------------------------------------------
  def getDuration(self) :
    return(self.duration)
