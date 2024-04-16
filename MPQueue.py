import os
import sys
import atexit
import multiprocessing 
import datetime 
from multiprocessing import Process,Queue
from multiprocessing import JoinableQueue
import logging
import time
import traceback

# custom process class
class MPQueue(Process):


  #---------------------------------------------------------------------------------------------
  def __init__(self,args,parms) :
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    logging.info(f'Queue Reader __init__ queue {self}')
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
    self.runningWorkers={}
    self.busyWorkers={}
    self.queueHwm=0
    self.thruHwm=0
    self.queueFeeders=0
    self.queueHwmTime=datetime.datetime.now()
    self.thruHwmTime=datetime.datetime.now()
    self.jtlName=f'pylogen-{self.thruHwmTime.strftime("%Y-%m-%d-%H:%M:%S")}.jtl'
    self.jtlFile=open(self.jtlName,"w")
    self.last=time.time()
    #self.queue=Queue()
    self.queue=Queue()
    logging.info(f'Queue Reader created queue {self}')

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
    try :
      print(f'Queue Reader Starting {self.name} args={self.args} parms={self.parms}')
      logging.warning(f'Queue Reader Starting {self.name} args={self.args} parms={self.parms}')
      self.last=time.time()
      while True :
        try :
          msg = self.queue.get()
          msg["_qSize"] = self.queue.qsize()
          self.processMsg(msg)
        except KeyboardInterrupt:
          print("Caught KeyboardInterrupt, terminating Queue Reader")
          break
      self.over()
    except Exception as e :
      logging.exception(f'{e}',stack_info=True,exc_info=True)

  #---------------------------------------------------------------------------------------------
  def oh(self):
    print(f'Oh !! CTRL-C')

  #---------------------------------------------------------------------------------------------
  def over(self):
    thruHwmTime=self.thruHwmTime.strftime("%Y-%m-%d %H:%M:%S")
    queueHwmTime=self.queueHwmTime.strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f'QueueReader stopped processed {self.opCount} ThruHighwatermark {self.thruHwm:9.2f} at {self.thruHwmTime} QueueHighwatermark {self.queueHwm} at {self.queueHwmTime}')
    #self.exit.set()
    #os._exit(os.EX_OK)
    sys.exit()

  #---------------------------------------------------------------------------------------------
  def processReportMsg(self,msg) :
    #print(f'processReportMsg() starting {m}')
    m=msg["msg"]
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
    if msg["_qSize"] > self.queueHwm : 
      self.queueHwm = msg["_qSize"]
      self.queueHwmTime = datetime.datetime.now()
    #print(f'processReportMsg() ending {m}')
    self.out(msg)

  #---------------------------------------------------------------------------------------------
  def processCmdMsg(self,msg) :
    m=msg["msg"]
    logging.info(f'{m=}')
    logging.info(f'{msg=}')
    if m["cmd"].startswith("set ") :
      logging.info(f'set command')
      t=m["cmd"].split()
      #print(f'{t}')
      if t[1] == "summary" :
        #print(f'setting summary cal {self.opCount} {self.opThresh}')
        self.opThresh=int(t[2])
    if m["cmd"] == "addfeeder" :
        self.queueFeeders += 1
    elif m["cmd"] == "removefeeder" :
        self.queueFeeders -= 1
    elif m["cmd"] == "stop" :
      if self.queueFeeders == 0 :
        logging.info(f'stop msg {self.queueFeeders=}, MPQueue over')
        self.over()
    logging.info(f'{self.queueFeeders=}')

  #---------------------------------------------------------------------------------------------
  def processActivityMsg(self,msg) :
     m=msg["msg"]
     if "runningWorkers" in m :
       if msg["id"] not in self.runningWorkers :
         self.runningWorkers[msg["id"]] = 0
       self.runningWorkers[msg["id"]] += m["runningWorkers"]
     elif "busyWorkers" in m :
       if msg["id"] not in self.busyWorkers :
         self.busyWorkers[msg["id"]] = 0
       self.busyWorkers[msg["id"]] += m["busyWorkers"] 
     else :
       logging.error("Unknown activity msg {msg}")
     logging.debug(f'{self.busyWorkers=} {self.runningWorkers=}')

#---------------------------------------------------------------------------------------------
  def processMsg(self,m) :
    now=datetime.datetime.now()
    #m["_queueNow"]=now
    m["_queueNow"]=f'{now}'
    m["_queueNowEpoch"]=now.timestamp()
    m["_queueTime"]=now.timestamp() - m["epoch"]

    logging.debug(f'Got msg {m}') 
    if "type" in m :
      if  m["type"] == "report" :
        self.processReportMsg(m)
      elif m["type"] == "error" :
        print(f'{m}',file=sys.stderr) 
      elif m["type"] == "cmd" :
        self.processCmdMsg(m)
      elif m["type"] == "activity" :
        #print(f'processMsg() received {m}')
        self.processActivityMsg(m)
        #logging.info(f'msg {m}')
      elif m["type"] == "runner" :
        #logging.info(f'msg {m}')
        if  m["action"] == "start" :
          self.startedCuts += 1
          self.activeCuts += 1
        elif  m["action"] == "end" :
          self.endedCuts += 1
          self.activeCuts -= 1
        else :
          pass
    else :
       logging.info(f'{m}',file=sys.stderr) 

   
  #---------------------------------------------------------------------------------------------
  def outJtl(self,msg) :
    # timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
    #2024-04-15 18:54:15.743 1713200055.744 report          3      0.49        0        0        0 CLO_DUM2.27164.Dummy.0.RMngr.R_0         req        None            1      1.00 RC 0 step 0     t 1.001
    #2024-04-15 18:54:16.810 1713200056.810 report          4      2.72        0        0        0 OPE_DUM1:27170.27172.Dummy.0.RMngr.R_0   req        None            1      0.49 RC 0 step 0     t 1.001
    #2024-04-15 18:54:16.821 1713200056.821 report          5      2.72        0        0        0 OPE_DUM2:27174.27180.Dummy.0.RMngr.R_0   req        None            1      0.49 RC 0 step 0     t 1.001

    #2024-04-15 18:54:35,782 pid=27152 MPQueue-1 MainThread MPQueue root  processMsg 153 DEBUG Got msg {'type': 'report', 'from': 'worker', 'time': '2024-04-15 18:54:35.782029', 'epoch': 1713200075.782029, 'pid': 27167, 'id': 'CLO_DUM2.27167', 'msg': {'time': '2024-04-15 18:54:34.780510', 'epoch': 1713200074.78051, 'fullId': 'CLO_DUM2.27167.Dummy.0.RMngr.R_0', 'opcount': 4, 'nature': 'req', 'transactionId': 'None', 'thru': 0.33281953974092265, 'rc': 0, 'step': '0', 'delta': 1.001377820968628}, '_qSize': 0, '_queueNow': datetime.datetime(2024, 4, 15, 18, 54, 35, 782257)}
    #2024-04-15 18:54:21,830 pid=27152 MPQueue-1 MainThread MPQueue root  processMsg 153 DEBUG Got msg {'type': 'report', 'from': 'worker', 'time': '2024-04-15 18:54:21.829941', 'epoch': 1713200061.829941, 'pid': 27199, 'id': 'OPE_DUM2:27174.27199', 'msg': {'time': '2024-04-15 18:54:20.828178', 'epoch': 1713200060.828178, 'fullId': 'OPE_DUM2:27174.27199.Dummy.0.RMngr.R_0', 'opcount': 1, 'nature': 'req', 'transactionId': 'None', 'thru': 0.165883936329548, 'rc': 0, 'step': '0', 'delta': 1.0012710094451904}, '_qSize': 0, '_queueNow': datetime.datetime(2024, 4, 15, 18, 54, 21, 830359)}



    m=msg["msg"]
    timeStamp=f'{m["time"][:-3]}'
    elapsed=f'{m["delta"]:5.3f}'
    label=f'{m["fullId"]:40s}'
    responseCode=f'{m["rc"]}'
    responseMessage==f''
    threadName=f'{m["fullId"]:40s}'
    dataType=f''
    success=f'{m["rc"]}'
    failureMessage=f''
    bytes=f'1000'
    sentBytes=f'1000'
    grpThreads=f'1000'
    allThread=f'1000'
    URL=f'{m["fullId"]:40s}'
    Latency=f'{m["delta"]:5.3f}'
    IdleTime=f'0'
    Connect=f'0'
   
  #---------------------------------------------------------------------------------------------
  def out(self,msg) :
    m=msg["msg"]
    if self.args.outformat == 'short' :
      self.jtlFile.write((f'{m["time"][:-3]} {m["epoch"]:14.3f} {msg["type"]:8s}'
            f' {self.opCount:8d} {self.thru:9.2f}'
            f' {self.startedCuts:8d} {self.endedCuts:8d} {self.activeCuts:8d}'
            f' {m["fullId"]:40s} {m["nature"]:10} {m["transactionId"]:10s}'
            f' {m["opcount"]:6d} {m["thru"]:9.2f} RC {m["rc"]} step {m["step"]:5s} t {m["delta"]:5.3f}'
            f'\n'
           ))
    elif self.args.outformat == 'raw' :
      self.jtlFile.write((f"{m}\n"))
    elif self.args.outformat == 'jtl' :
      # timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,sentBytes,grpThreads,allThreads,URL,Latency,IdleTime,Connect
      self.outJtl(msg)
    else : 
      self.jtlFile.write((f'{m["time"][:-3]} typ {msg["type"]:8s}'
            f' {msg["_qSize"]:6d} ops {self.opCount:8d} gThru {self.thru:9.2f}'
            f' sta {self.startedCuts:8d} end {self.endedCuts:8d} act {self.activeCuts:8d}'
            f' pid {m["pid"]:6d} fullId {m["fullId"]:40s} kind {m["nature"]:10} transId {m["transactionId"]:10s}'
            f' opcount {m["opcount"]:6d} thru {m["thru"]:9.2f} RC {m["rc"]} step {m["step"]:5s} t {m["delta"]:5.3f}'
            f'\n'
           ))
    self.jtlFile.flush()
   
