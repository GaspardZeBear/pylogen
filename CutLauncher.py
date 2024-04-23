import logging
import importlib
from multiprocessing.shared_memory import SharedMemory
from ClassUnderTest import *
from MPRunner import *

#------------------------------------------------------------------------------
# closedModel
# Dynamically create an instance of args.action as cut and starts a runner process
#------------------------------------------------------------------------------
class CutLauncher() :

  def __init__(self,args,parms):
    logging.debug(f'CutLauncher will create a MPRunner')
    mpRunner=MPRunner(args,parms)
    logging.debug(f'CutLauncher created a MPRunner')
    mpRunner.daemon=True
    logging.debug(f'CutLauncher will start MPRunner')
    mpRunner.start()
    logging.debug(f'CutLauncher started MPRunner')
