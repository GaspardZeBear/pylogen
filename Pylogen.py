import datetime
import time
import sys
import re
import random
import argparse
import multiprocessing
import logging
import importlib
import json
from multiprocessing.shared_memory import SharedMemory
from ClassUnderTest import *
from Runner import *
from Defaults import *
from MPRunner import *
from MPQueue import *
from OPController import *
from OPGenerator import *
from CutLauncher import *

#------------------------------------------------------------------------------
# closedModel
# Dynamically create an instance of args.action as cut and starts a runner process
#------------------------------------------------------------------------------
def closedModel(args,resultQueue):
  logging.warning(f'Launching {args.action}')
  parms={"queue":resultQueue,"delay":int(args.postpone)}
  parms["controllerQueue"]=None
  parms["generatorQueue"]=None
  for i in range(0,int(args.process)) :
    logging.info(f'Launching {args.action}')
    CutLauncher(args,parms)
    parms["delay"] += int(args.rampup) 

#------------------------------------------------------------------------------
# openedModel
#------------------------------------------------------------------------------
def openedModel(args,resultQueue):
  logging.warning(f'Launching {args.action}')
  #print(f'Launching {args.action}')
  parms={"queue":resultQueue,"delay":int(args.postpone)}
  parms["jobsQueue"]=Queue()
  parms["controllerQueue"]=Queue()
  parms["generatorQueue"]=Queue()
  controller=OPController(args,parms)
  controller.daemon=False
  controller.start()
  generator=OPGenerator(args,parms)
  generator.daemon=True
  generator.start()


#-----------------------------------------------------
# A scenrio is a file containing commands lines .. so loop on this file
# Don't use logging !
#-----------------------------------------------------
def fScenario(args) :
  print(f'Playing {args.file}')
  lineno=1
  with open(args.file) as fIn :
    for l in fIn.readlines() :
      logging.info(l[:-1])
      nl=l[:-1].lstrip()
      if nl.startswith("#") :
        logging.info(f'<{nl[:-1]}> discard #')
        continue
      if len(nl) ==0 :
        logging.info(f'<{nl[:-1]}> discard 0')
        continue
      myParser(args.queue,l[:-1],lineno)
      lineno += 1

#------------------------------------------------------------------------------
def myParser(queue,input,lineno) :
  print(f'myParser()  Starting : {input=}')
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument('-v', '--verbose',
                    action='count',
                    dest='verbose',
                    default=0,
                    help="verbose output (repeat for increased verbosity)")
  parser.add_argument('action',       help="",default="Default.action")
  parser.add_argument('--defaults',   help="",default="defaults.json")
  parser.add_argument('--process',    help="",default=Defaults.process)
  parser.add_argument('--postpone',   help="",default=Defaults.postpone)
  parser.add_argument('--rampup',     help="",default=Defaults.rampup)
  parser.add_argument('--duration',   help="",default=Defaults.duration)
  parser.add_argument('--loops',      help="",default=Defaults.loops)
  parser.add_argument('--shmsize',    help="",default=Defaults.shmsize)
  parser.add_argument('--steps',    help="",default=Defaults.steps)
  parser.add_argument('--prefork',    help="",default=Defaults.prefork)
  parser.add_argument('--extra',      help="",default=Defaults.extra)
  parser.add_argument('--pauseloop',  help="",default=Defaults.pauseloop)
  parser.add_argument('--pausestep', help="",default=Defaults.pausestep)
  parser.add_argument('--summary',    help="",default=Defaults.summary)
  parser.add_argument('--outformat',  help="",default=Defaults.outformat)
  parser.add_argument('--id',         help="",default=Defaults.id)
  parser.add_argument('-f','--file', action="store",help="scenario")


  # integration open model
  parser.add_argument('--openedmodel',   help="",action="store_true")
  parser.add_argument('--controllerDelay',   help="",default="5")
  parser.add_argument('--generatorDelay',   help="",default="1")
  parser.add_argument('--burst',   help="",default="1")
  parser.add_argument('--schedule',   help="",default="30@10,30@20,30@30")
  parser.add_argument('--workerDelay',   help="",default="1")
  parser.add_argument('--trigger',   help="",default="3")
  parser.add_argument('--decrease',   help="",default="10")

  print(f'myParser()  parser initialized ')

  # --------
  # len(input)==0 means argparse will use sys.argv
  # else line read from file, still to be parsed
  # --------
  if len(input) == 0 :
    args=parser.parse_args()
  else :
    cmdLine=re.split('\s+',input)
    print(f'myParser() len(input) > 0 : {input=} {cmdLine=}')
    args=parser.parse_args(cmdLine)

  #args.id=f'{args.id}-{lineno}'
  print(f"myParser() got args {args=}")
  loglevels=[logging.ERROR,logging.WARNING,logging.INFO,logging.DEBUG,1]
  loglevel=loglevels[args.verbose] if args.verbose < len(loglevels) else loglevels[len(loglevels) - 1]
  logging.basicConfig(force=True,format="%(asctime)s pid=%(process)d %(processName)s %(threadName)s %(module)s %(name)s  %(funcName)s %(lineno)s %(levelname)s %(message)s", level=loglevel)
  logging.info(f'Loglevel {loglevel=}  called logging.basicConfig, loggin can be used')

  args.queue=queue
  queue.setArgs(args)
  # ---------------------------------------------------------------------------------------------
  # !!! start as late as possible, after setting args  (else : other process and args not settable)
  # hard to detect is started, Exception easiest :)
  # When started, only way to change is thru a queue message
  # ---------------------------------------------------------------------------------------------
  try :
    queue.start()
  except Exception as e :
    logging.exception(f'{e} may be normal')
  finally :
    if args.action != "scenario" :
      cmd=f'set summary {args.summary} id {args.id}'
      queueSender.sendMsgToQueue('cmd',{'cmd':cmd})
  if args.action == "scenario" :
    logging.info(f'Scenario to be processed')
    fScenario(args)
  else :
    print(f'args : {args}')
    if args.openedmodel :
      openedModel(args,args.queue)
    else :
      closedModel(args,args.queue)

#------------------------------------------------------------------------------
if __name__ == "__main__":
  Defaults.init()
  queue=MPQueue(None,None)
  queueSender=QueueSender("main","main",queue)
  queue.daemon=False
  myParser(queue,'',0)
  time.sleep(5)
  while True :
    children=multiprocessing.active_children() 
    if  len(children) == 1 :
      queueSender.sendMsgToQueue('cmd',{'cmd':'stop'})
      break
    time.sleep(5)
  print("Start waiting for queue reader")
  while len(multiprocessing.active_children()) > 0 :
    print("Waiting for queue reader")
    time.sleep(1)
  sys.exit()
