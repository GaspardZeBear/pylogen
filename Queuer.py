# example of using the queue with processes
from time import sleep
from random import random
import multiprocessing 
from multiprocessing import Process
from multiprocessing import Queue
from MPQueue  import *
from datetime  import *

class Q() :
  def __init__(self) :
    self.t=time
  def getT(self) :
    self.t=time
    return(self)
  def getTJson(self) :
    name=multiprocessing.current_process().name
    return({
      "name":name,
      "t":datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    })
 
# generate work
def producer(queuer):
    print('Producer: Running', flush=True)
    # generate work
    for i in range(1000):
        value = Q().getTJson()
        sleep(0.01)
        queuer.putQueue(value)
    queuer.putQueue(None)
    print('Producer: Done', flush=True)
 
# entry point
if __name__ == '__main__':
    # create the shared queue
    qr=MPQueue(None,None)
    q=qr.getQueue()
    qr.start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    Process(target=producer, args=(qr,)).start()
    #producer_process = Process(target=producer, args=(qr,))
    #producer_process.start()
