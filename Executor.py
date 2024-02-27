from Request import *
import time
import logging

class Executor() :

  #@staticmethod
  def exec(func) :
 
    #---------------------------------------------------------------------------------------
    #--- Lots of Ugly things to be improved
    #---------------------------------------------------------------------------------------
    def wrapper(*args,**kwargs) :
      logging.debug(f'wrapper args {args} kwargs {kwargs}')
      #logging.warning(f'wrapper kwargs {kwargs}')
      #logging.warning(f'type {type(args[0])}')
      if isinstance(args[0],Request) :
        #logging.warning("Direct call")
        r=args[0]
        method=False
      elif isinstance(args[1],Request) :
        #logging.warning("Call from an objet")
        r=args[1]
        method=True
      else :
        logging.warning("Mystery caller")
        pass
      rc=0
      try :
        r.launch()
        if method :
          func(args[0],*args[2:])
        else :
          func(*args[1:])
      except Exception as e :
        logging.error(f'Executor exception : {e}')
        r.setError(f'{e}')
        rc=16
      r.stop()
      r.setRc(rc)
    return(wrapper)
