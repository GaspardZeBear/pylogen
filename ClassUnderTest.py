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
    self.step=None
    self.ctx={}
    #self.reset()

  #-------------------------------------------------------------------
  def resetBeforeStep(self) :
    self.requestsManager=RequestsManager('RMngr')

  #-------------------------------------------------------------------
  def resetBeforeSteps(self) :
    self.ctx={}

  #-------------------------------------------------------------------
  def getRequestsManager(self) :
    return(self.requestsManager)

  def genDatas(self) :
    #self.datas=''.join(random.choices(string.ascii_letters, k=length))
    #print("to be implemented")
    pass

  def setRunner(self,runner) :
    self.runner=runner

  def setTransaction(self,transaction=True) :
    self.runner.setTransaction(transaction)

  def setDatas(self,datas) :
    self.datas=datas

  def addCtx(self,key,datas) :
    self.ctx[key]=datas

  def getCtx(self,key=None) :
    if key is None :
      return(self.ctx)
    else :
      try :
        return(self.ctx[key])
      except Exception as e :
        return(None)

  def setStep(self,step) :
    self.step=step

  def getStep(self) :
    return(self.step)

  def processDatas(self) :
    pass

  def getDatas(self) :
    return(self.datas)

  def func(self) :
    print("to be implemented")


