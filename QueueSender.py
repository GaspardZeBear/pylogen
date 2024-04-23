import re
import os
import time
import datetime
import logging
from datetime import datetime,timedelta
from multiprocessing import Queue
from MPQueue import *


class QueueSender() :

  #----------------------------------------------------------------------
  def __init__(self,source,id,destination) :
    self.source=source
    self.queue=destination
    self.id=id
    self.pid=os.getpid()

  #----------------------------------------------------------------------
  def sendMsgToQueue(self,type,msg) :
    now=datetime.datetime.now()
    t=now.strftime("%Y-%m-%d %H:%M:%S.%f")
    te=now.timestamp()
    msg1={
       "type" : type ,
       "from" : self.source,
       "time" : t,
       "epoch" : te,
       "pid" : self.pid,
       "id" : self.id,
       "msg" : msg
       }
    self.queue.putQueue(msg1)


