import multiprocessing 
from multiprocessing import Process,Event
import logging
import time
from Runner import *
from ClassUnderTest import *

# custom process class
class MPRunner(Process):
  def __init__(self,args,parms,cut) :
    logging.info(f'MPRunner init() args={args} ')
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.args=args
    self.parms=parms
    logging.info(f'MPRunner init() name={self.name} ')
    pName=self.name.split(':')[0]
    #self.parms["pNum"]=str(int(self.name.split('-')[1]) -1)
    self.parms["pNum"]=str(int(pName.split('-')[1]) -1)
    self.parms["childClassName"]=cut.__class__.__name__
    self.cut=cut
    logging.info(f'MPRunner {self.name}  created')

  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args} parms={self.parms}')
      time.sleep(self.parms["delay"])
      logging.info(f'Creating runner')
      runner=Runner(self.args,self.parms)
      logging.info(f' runner created')
      self.parms["runner"]=runner
      self.cut.setRunner(runner)
      runner.loop(self.cut)
      logging.info(f'End of {self.name} args={self.args} parms={self.parms}')
      self.exit.set()
    except KeyboardInterrupt:
      print(f"Caught KeyboardInterrupt, terminating {self.__class__.__name__}")


