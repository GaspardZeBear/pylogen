import datetime
from datetime import *
import time
import logging
from Request import *

#------------------------------------------------------------------------
class RequestsManager() :

  def __init__(self,name) :
    self.name=name
    self.requests=[]
    self.requestsDict={}
    self.rc=-1
    self.duration=0
    self.elapsed=0
    logging.debug(f" requestsManager {self.name} created")

  #------------------------------------------------------------------------
  def newRequest(self,name) :
    r=Request(name)
    if name not in self.requestsDict :
      self.requests.append(r)
      self.requestsDict[name]=len(self.requests)-1
    else :
      raise Exception(f"Request with name {name} already exists")
    return(r)

  #------------------------------------------------------------------------
  def setName(self,name) :
    self.name=name

  #------------------------------------------------------------------------
  def getName(self) :
    return(self.name)

  #------------------------------------------------------------------------
  def getRequests(self) :
    return(self.requests)

  #------------------------------------------------------------------------
  def getRequestByIndex(self,idx) :
    return(self.requests[idx])

  #------------------------------------------------------------------------
  def getRequestByName(self,name) :
    return(self.requests[self.requestsDict[name]])

  #------------------------------------------------------------------------
  def getRequestIndex(self,name) :
    return(self.requestsDict[name])

  #------------------------------------------------------------------------
  def close(self) :
    self.getDuration()
    self.getRc()

  #------------------------------------------------------------------------
  def getDuration(self) :
    self.duration=0
    for r in self.requests :
      logging.debug(f'{r} {r.getDuration()}')
      self.duration += r.getDuration()
    return(self.duration)

  #------------------------------------------------------------------------
  def getRc(self) :
    for r in self.requests :
      if r.getRc() > self.rc :
        self.rc = r.getRc()
    return(self.rc)


