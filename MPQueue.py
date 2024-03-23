import os
import sys
import atexit
import multiprocessing 
import datetime 
from multiprocessing import Process,Queue
import logging
import time

# custom process class
class MPQueue(Process):


  #---------------------------------------------------------------------------------------------
  def __init__(self,args,parms) :
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    #atexit.register(self.over)
    #atexit.register(self.oh)
    self.args=args
    self.parms=parms
    self.opCount=0
    self.opCountLast=0
    self.opThresh=100
    self.summary=100
    self.thru=0
    self.startedCuts=0
    self.endedCuts=0
    self.activeCuts=0
    self.queueHwm=0
    self.thruHwm=0
    self.queueHwmTime=datetime.datetime.now()
    self.thruHwmTime=datetime.datetime.now()
    self.jtlName=f'pylogen-{self.thruHwmTime.strftime("%Y-%m-%d-%H:%M:%S")}.jtl'
    self.jtlFile=open(self.jtlName,"w")
    self.last=time.time()
    self.queue=Queue()
    #print(f'Queue Reader created queue {self}')

  #---------------------------------------------------------------------------------------------
  def setArgs(self,args):
    self.args=args
    #print(f'Queue setArgs : {args}')

  #---------------------------------------------------------------------------------------------
  def getQueue(self):
    return(self.queue)

  #---------------------------------------------------------------------------------------------
  def putQueue(self,val):
    self.queue.put(val)

  #---------------------------------------------------------------------------------------------
  def run(self):
    logging.info(f'Queue Reader Starting {self.name} args={self.args} parms={self.parms}')
    self.last=time.time()
    while True :
      try :
        msg = self.queue.get()
        msg["_qSize"] = self.queue.qsize()
        self.processMsg(msg)
      except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating Queue Reader")
        break
      except Exception as e :
        print(f'Queue reader stopped {e}')
        break
    self.over()

  #---------------------------------------------------------------------------------------------
  def oh(self):
    print(f'Oh !! CTRL-C')

  #---------------------------------------------------------------------------------------------
  def over(self):
    thruHwmTime=self.thruHwmTime.strftime("%Y-%m-%d %H:%M:%S")
    queueHwmTime=self.queueHwmTime.strftime("%Y-%m-%d %H:%M:%S")
    print(f'QueueReader stopped processed {self.opCount} ThruHighwatermark {self.thruHwm:9.2f} at {self.thruHwmTime} QueueHighwatermark {self.queueHwm} at {self.queueHwmTime}')
    #self.exit.set()
    #os._exit(os.EX_OK)
    sys.exit()

  #---------------------------------------------------------------------------------------------
  def processMsg(self,m) :
    now=datetime.datetime.now()
    m["queueNow"]=now
    if "type" in m :
      if  m["type"] == "report" :
        if  m["nature"] == "req" :
          self.opCount += 1
        now=time.time()
        interval=now - self.last
        if (interval > self.opThresh) :
          self.thru = (self.opCount - self.opCountLast) / interval
          self.last=now
          self.opCountLast=self.opCount
          if self.thru > self.thruHwm : 
            self.thruHwm = self.thru
            self.thruHwmTime = datetime.datetime.now()
        if m["_qSize"] > self.queueHwm : 
          self.queueHwm = m["_qSize"]
          self.queueHwmTime = datetime.datetime.now()
        self.out(m)
      elif m["type"] == "error" :
        print(f'{m}',file=sys.stderr) 
      elif m["type"] == "cmd" :
        if m["cmd"].startswith("set ") :
          t=m["cmd"].split()
          #print(f'{t}')
          if t[1] == "summary" :
            #print(f'setting summary cal {self.opCount} {self.opThresh}')
            self.opThresh=int(t[2])
        if m["cmd"] == "stop" :
          self.over()
      elif m["type"] == "runner" :
        if  m["action"] == "start" :
          logging.info(f'msg {m}')
          self.startedCuts += 1
          self.activeCuts += 1
        elif  m["action"] == "end" :
          logging.info(f'msg {m}')
          self.endedCuts += 1
          self.activeCuts -= 1
        else :
          pass
    else :
       logging.info(f'{m}',file=sys.stderr) 

   
  #---------------------------------------------------------------------------------------------
  def out(self,m) :
    if self.args.outformat == 'short' :
      self.jtlFile.write((f'{m["time"][:-3]} {m["epoch"]:14.3f} {m["type"]:8s}'
            f' {self.opCount:8d} {self.thru:9.2f}'
            f' {self.startedCuts:8d} {self.endedCuts:8d} {self.activeCuts:8d}'
            f' {m["fullId"]:40s} {m["nature"]:10} {m["transactionId"]:10s}'
            f' {m["opcount"]:6d} {m["thru"]:9.2f} RC {m["rc"]} len {m["length"]:5d} t {m["delta"]:5.3f}'
            f'\n'
           ))
    elif self.args.outformat == 'raw' :
      self.jtlFile.write((f"{m}\n"))
    else : 
      self.jtlFile.write((f'{m["time"][:-3]} typ {m["type"]:8s}'
            f' {m["_qSize"]:6d} ops {self.opCount:8d} gThru {self.thru:9.2f}'
            f' sta {self.startedCuts:8d} end {self.endedCuts:8d} act {self.activeCuts:8d}'
            f' pid {m["pid"]:6d} fullId {m["fullId"]:40s} kind {m["nature"]:10} transId {m["transactionId"]:10s}'
            f' opcount {m["opcount"]:6d} thru {m["thru"]:9.2f} RC {m["rc"]} len {m["length"]:5d} t {m["delta"]:5.3f}'
            f'\n'
           ))
    self.jtlFile.flush()
   
