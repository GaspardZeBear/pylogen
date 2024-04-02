import multiprocessing 
from multiprocessing import Process,Event
import logging
import time
import os
from Runner import *
from ClassUnderTest import *

# custom process class
class MPRunner(Process):
  def __init__(self,args,parms,cut) :
    logging.debug(f'MPRunner init() args={args} ')
    logging.debug(f'MPRunner init() parms={parms} ')
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.args=args
    self.parms=parms
    logging.debug(f'MPRunner init() name={self.name} ')
    pName=self.name.split(':')[0]
    #self.parms["pNum"]=str(int(self.name.split('-')[1]) -1)
    self.parms["pNum"]=str(int(pName.split('-')[1]) -1)
    self.parms["childClassName"]=cut.__class__.__name__
    self.cut=cut
    logging.debug(f'MPRunner {self.name}  created')

  def run(self):
    try :
      logging.debug(f'Starting {self.name} args={self.args} parms={self.parms}')
      #self.parms["queue"].putQueue({"type":"runner","action":"start","cut":self.parms["childClassName"]})
      #----------------------------------------------------------------------
      self.parms["queue"].putQueue({ 
        "type" : "activity",
        "from" : "worker",
        "id" : os.getpid(),
        "cut":self.parms["childClassName"],
        "runningWorkers" : 1
      })

      time.sleep(self.parms["delay"])
      logging.debug(f'Creating runner')
      runner=Runner(self.args,self.parms)
      logging.debug(f' runner created')
      self.parms["runner"]=runner
      self.cut.setRunner(runner)
      runner.loop(self.cut)
      #self.parms["queue"].putQueue({"type":"runner","action":"end","cut":self.parms["childClassName"]})
      self.parms["queue"].putQueue({ 
        "type" : "activity",
        "from" : "worker",
        "id" : os.getpid(),
        "cut":self.parms["childClassName"],
        "runningWorkers" : -1
      })
      logging.debug(f'End of {self.name} args={self.args} parms={self.parms}')
      self.exit.set()
    except KeyboardInterrupt:
      print(f"Caught KeyboardInterrupt, terminating {self.__class__.__name__}")
    except Exception as e :
      logging.exception(f'{e}',stack_info=True,exc_info=True)
      print(f'MPRunner exception stopped {e}')




