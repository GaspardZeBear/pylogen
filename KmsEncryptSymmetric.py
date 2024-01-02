from google.cloud import kms
import base64
import datetime
import time
import sys
import re
import hashlib
import logging
import json
from ClassUnderTest import *
from RequestsManager import *
from Executor import *


class KmsEncryptSymmetric(ClassUnderTest) :

  def __init__(self,args,parms) :
    logging.info("starting")
    super().__init__(args,parms)
    self.extra=json.loads(self.args.extra)
    try :
      self.client=kms.KeyManagementServiceClient()
      self.key_version_name=self.client.crypto_key_version_path(args.project_id, args.location_id, args.key_ring_id, args.crypto_key_id, args.version_id)
    except Exception as e :
      logging.error(f'{e}')
      #self.runner.sendError(f'{e}')

  #-------------------------------------------------------------------
  def processDatas(self) :
    pass

  #-------------------------------------------------------------------
  def func(self) :
    try :
      self.encryptSymmetric(self.requestsManager.newRequest("R-Encrypt"),self.client,self.key_version_name,self.getDatas())
    except Exception as e :
      logging.error(f'{e}')
      self.runner.sendError(f'{e}')

  @Executor.exec
  #-------------------------------------------------------------------
  # Note : on encryp : No raw encrypt in python (no client.rawEncrypt method !
  def encryptSymmetric(self,client, name, plaintext):
    response = client.encrypt(request={'name': name, 'plaintext': plaintext})

