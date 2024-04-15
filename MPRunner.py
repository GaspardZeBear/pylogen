import importlib
import multiprocessing 
from multiprocessing import Process,Event
import logging
import time
import os
from Runner import *
from ClassUnderTest import *

# custom process class
class MPRunner(Process):
  def __init__(self,args,parms) :
    logging.debug(f'MPRunner init() args={args} ')
    logging.debug(f'MPRunner init() parms={parms} ')
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.args=args
    self.queue=self.args.queue
    self.parms=parms
    logging.debug(f'MPRunner init() name={self.name} ')
    pName=self.name.split(':')[0]
    #self.parms["pNum"]=str(int(self.name.split('-')[1]) -1)
    self.parms["pNum"]=str(int(pName.split('-')[1]) -1)
    qualifiers=args.action.split('.')
    obj=qualifiers[-1]

    self.cut=getattr(importlib.import_module(args.action), obj)(args,parms)
    self.parms["childClassName"]=self.cut.__class__.__name__
    logging.debug(f'MPRunner {self.name}  created')

  def run(self):
    try :
      self.parms["queue"].putQueue({'type':'cmd','cmd':'addfeeder','id':os.getpid()})
      logging.info(f'Start of {self.name} args={self.args} parms={self.parms}')
      self.parms["queue"].putQueue({ 
        "type" : "activity",
        "from" : "worker",
        "pid" : os.getpid(),
        "id" : self.args.id,
        "cut":self.parms["childClassName"],
        "runningWorkers" : 1
      })

      time.sleep(self.parms["delay"])
      runner=Runner(self.args,self.parms)
      self.parms["runner"]=runner
      self.cut.setRunner(runner)
      runner.loop(self.cut)
      logging.info(f'removefeeder')
      self.parms["queue"].putQueue({ 
        "type" : "activity",
        "from" : "worker",
        "pid" : os.getpid(),
        "id" : self.args.id,
        "cut":self.parms["childClassName"],
        "runningWorkers" : -1
      })
      logging.info(f'End of {self.name} args={self.args} parms={self.parms}')
      logging.info(f'removefeeder')
      logging.info(f'Will send msg removefeeder')
      self.parms["queue"].putQueue({'type':'cmd','cmd':'removefeeder','id':os.getpid()})
      self.exit.set()
    #except KeyboardInterrupt:
    #  print(f"Caught KeyboardInterrupt, terminating {self.__class__.__name__}")
    except Exception as e :
      logging.exception(f'{e}',stack_info=True,exc_info=True)
      print(f'MPRunner exception stopped {e}')
    finally:
      #self.queue.putQueue({'type':'cmd','cmd':'removefeeder'})
      pass




