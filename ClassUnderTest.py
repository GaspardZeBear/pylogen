import random
import string
from RequestsManager import *

#-------------------------------------------------------------------
class ClassUnderTest() :

  def __init__(self,args,parms) :
    self.args=args
    self.parms=parms
    self.datas=None
    self.runner=None
    self.reset()

  #-------------------------------------------------------------------
  def reset(self) :
    self.requestsManager=RequestsManager('RMngr')

  #-------------------------------------------------------------------
  def getRequestsManager(self) :
    return(self.requestsManager)

  def genDatas(self,length) :
    self.datas=''.join(random.choices(string.ascii_letters, k=length))

  def setRunner(self,runner) :
    self.runner=runner

  def setTransaction(self,transaction=True) :
    self.runner.setTransaction(transaction)

  def setDatas(self,datas) :
    self.datas=datas

  def processDatas(self) :
    pass

  def getDatas(self) :
    return(self.datas)

  def func(self) :
    print("to be implemented")


