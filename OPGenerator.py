import multiprocessing
from multiprocessing import Process,Event,Queue
import logging
import time

# custom process class
class OPGenerator(Process):
  def __init__(self,args) :
    Process.__init__(self)
    self.exit = multiprocessing.Event()
    self.name="Generator"
    self.args=args
    self.jobsQueue=self.args.jobsQueue
    self.generatorDelay=float(self.args.generatorDelay)
    self.schedules=self.args.schedule.split(',')


  def run(self):
    try :
      logging.info(f'Starting {self.name} args={self.args}')
      count=0
      for schedule in self.schedules :
        logging.info(f' {self.name} {schedule}')
        duration,thru=schedule.split('@')
        #now=datetime.now()
        now = time.time()
        end=now + int(duration)
        while time.time() < end :
          time.sleep(1/float(thru))
          #logging.info(f'{self.name} event')
          self.jobsQueue.put({"x":None})
          count += 1
          if (count % 100) == 0 :
            logging.info(f'{self.name} {count=}')
    except Exception as e :
      print(f'{e}')

  def Xrun(self):
    try :
      logging.info(f'Starting {self.name} args={self.args}')
      count=0
      delay=self.generatorDelay
      while True :
        if count > self.burst :
          delay=self.generatorDelay/2
        if count > 2*self.burst :
          delay=self.generatorDelay
        time.sleep(delay)
        #logging.info(f'{self.name} event')
        self.jobsQueue.put({"x":None})
        count += 1
        if (count % 100) == 0 :
          logging.info(f'{self.name} {count=}')
    except Exception as e :
      print(f'{e}')


