import importlib
import multiprocessing 
from multiprocessing import Process,Event
import logging
import time
import os
from Runner import *
from ClassUnderTest import *
from QueueSender import *

# custom process class
class MPRunner(Process):
  def __init__(self,args,parms) :
    logging.debug(f'MPRunner init() args={args} ')
    logging.debug(f'MPRunner init() parms={parms} ')
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.args=args
    #self.args.id=f'{self.args.id}:{os.getpid()}'
    self.queue=self.args.queue
    self.parms=parms
    #self.id=self.args.id
    pName=self.name.split(':')[0]
    self.parms["pNum"]=str(int(pName.split('-')[1]) -1)
   
  def createCutProcess(self) : 
    qualifiers=self.args.action.split('.')
    obj=qualifiers[-1]
    self.args.id=f'{self.args.id}.{os.getpid()}'
    self.cut=getattr(importlib.import_module(self.args.action), obj)(self.args,self.parms)
    self.parms["childClassName"]=self.cut.__class__.__name__
    logging.debug(f'MPRunner {self.name}  created')

  def run(self):
    try :
      self.createCutProcess()
      self.queueSender=QueueSender("worker",self.args.id,self.queue)
      self.parms["queueSender"]=self.queueSender
      self.queueSender.sendMsgToQueue("cmd",{'cmd':'addfeeder','id':os.getpid()})
      logging.info(f'Start of {self.name} args={self.args} parms={self.parms}')
      self.queueSender.sendMsgToQueue("activity",{"cut":self.parms["childClassName"],"runningWorkers" : 1})
      time.sleep(self.parms["delay"])
      runner=Runner(self.args,self.parms)
      self.parms["runner"]=runner
      self.cut.setRunner(runner)
      runner.loop(self.cut)
      self.queueSender.sendMsgToQueue("activity",{"cut":self.parms["childClassName"],"runningWorkers" : -1})
      logging.info(f'End of {self.name} args={self.args} parms={self.parms}')
      self.queueSender.sendMsgToQueue("cmd",{'cmd':'removefeeder','id':os.getpid()})
      self.exit.set()
    #except KeyboardInterrupt:
    #  print(f"Caught KeyboardInterrupt, terminating {self.__class__.__name__}")
    except Exception as e :
      logging.exception(f'{e}',stack_info=True,exc_info=True)
      print(f'MPRunner exception stopped {e}')
    finally:
      #self.queue.putQueue({'type':'cmd','cmd':'removefeeder'})
      pass




