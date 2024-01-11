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

#------------------------------------------------------------------------------
# Dynamically create an instance of args.action as cut and starts a runner process
#------------------------------------------------------------------------------
def launch(args):
  parms={"queue":'','scoreboard':None,"delay":int(args.postpone)}
  for i in range(0,int(args.process)) :
    logging.info(f'Launchin {args.action}')
    qualifiers=args.action.split('.')
    obj=qualifiers[-1]
    scoreboard = SharedMemory(create=True, size=int(args.shmsize))
    parms["scoreboard"] = scoreboard
    scoreboards.append(scoreboard)
    cut=getattr(importlib.import_module(args.action), obj)(args,parms)
    mpRunner=MPRunner(args,parms,cut)
    mpRunner.daemon=True
    mpRunner.start()
    parms["delay"] += int(args.rampup) 

#-----------------------------------------------------
# A scenrio is a file containing commands lines .. so loop on this file
#-----------------------------------------------------
def fScenario(args) :
  print(f'Playing {args.file}')
  with open(args.file) as fIn :
    for l in fIn.readlines() :
      print(l[:-1])
      nl=l[:-1].lstrip()
      if nl.startswith("#") :
        print(f'<{nl[:-1]}> discard #')
        continue
      if len(nl) ==0 :
        print(f'<{nl[:-1]}> discard 0')
        continue
      myParser(args.queue,l[:-1])

#------------------------------------------------------------------------------
def myParser(queue,input) :
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
  parser.add_argument('--lengths',    help="",default=Defaults.lengths)
  parser.add_argument('--extra',      help="",default=Defaults.extra)
  parser.add_argument('--pauseloop',  help="",default=Defaults.pauseloop)
  parser.add_argument('--pauselen',   help="",default=Defaults.pauselen)
  parser.add_argument('--summary',    help="",default=Defaults.summary)
  parser.add_argument('--outformat',  help="",default=Defaults.outformat)
  parser.add_argument('--id',         help="",default=Defaults.id)
  parser.add_argument('-f','--file', action="store",help="scenario")

  # --------
  # len(input)==0 means argparse will use sys.argv
  # else line read from file, still to be parsed
  # --------
  if len(input) == 0 :
    args=parser.parse_args()
  else :
    cmdLine=re.split('\s+',input)
    print(f'{cmdLine}')
    args=parser.parse_args(cmdLine)

  loglevels=[logging.ERROR,logging.WARNING,logging.INFO,logging.DEBUG,1]
  loglevel=loglevels[args.verbose] if args.verbose < len(loglevels) else loglevels[len(loglevels) - 1]
  logging.basicConfig(format="%(asctime)s %(module)s %(name)s  %(funcName)s %(lineno)s %(levelname)s %(message)s", level=loglevel)
  logging.log(1,'Deep debug')
  args.queue=queue
  queue.setArgs(args)
  # ---------------------------------------------------------------------------------------------
  # !!! start as late as possible, after setting args  (else : other process and args not settable)
  # hard to detect is started, Exception easiest :)
  # When started, only way to change is thru a queue message
  # ---------------------------------------------------------------------------------------------
  try :
    summary=f'set summary {args.summary}'
    queue.start()
    queue.putQueue({'type':'cmd','cmd':summary})
  except Exception as e :
    print(f'{e}')
  if args.action == "scenario" :
    fScenario(args)
  else :
    print(f'args : {args}')
    launch(args)

#------------------------------------------------------------------------------
if __name__ == "__main__":
  Defaults.init()
  queue=MPQueue(None,None)
  queue.daemon=False
  scoreboards=[]
  #queue.start()
  myParser(queue,'')
  time.sleep(5)
  while True :
    children=multiprocessing.active_children() 
    #for c in children :
    #  print(f'{c}')
    if  len(children) == 1 :
      queue.putQueue({'type':'cmd','cmd':'stop'})
      break
    for scoreboard in scoreboards :
      try :
        myDictLen=int.from_bytes(scoreboard.buf[0:4],byteorder='big')
        myDictAsBytes=bytes(scoreboard.buf[4:]).decode()[:myDictLen]
        data = json.loads(myDictAsBytes)
        print(data)
      except Exception as e :
        print(f'{e}')
    time.sleep(5)
  print("All over, waiting for queue reader")
  while len(multiprocessing.active_children()) > 0 :
    print("Waiting for queue reader")
    time.sleep(1)
  sys.exit()
