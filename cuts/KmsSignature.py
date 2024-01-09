from google.cloud import kms
import base64
import datetime
import time
import sys
import re
import hashlib
import logging
import json
import cuts.KmsUtils
from ClassUnderTest import *
from RequestsManager import *
from Executor import *


class KmsSignature(ClassUnderTest) :

  def __init__(self,args,parms) :
    logging.info("starting")
    super().__init__(args,parms)
    self.keyparms=cuts.KmsUtils.parseExtra(self.args.extra)
    try :
      self.client=kms.KeyManagementServiceClient()
      #self.key_version_name=self.client.crypto_key_version_path(args.project_id, args.location_id, args.key_ring_id, args.crypto_key_id, args.version_id)
      self.key_version_name=self.client.crypto_key_version_path(
         self.keyparms["project_id"],
         self.keyparms["location_id"],
         self.keyparms["key_ring_id"],
         self.keyparms["crypto_key_id"],
         self.keyparms["version_id"]
         )
    except Exception as e :
      logging.error(f'{e}')

  #-------------------------------------------------------------------
  def processDatas(self) :
    message_bytes = self.datas.encode("utf-8")
    if "sha" in self.keyparms :
      sha=self.keyparms["sha"]
      if self.keyparms["sha"] == "sha384" :
        hash_ = hashlib.sha384(message_bytes).digest()
      elif self.keyparms["sha"] == "sha256" :
        hash_ = hashlib.sha256(message_bytes).digest()
      else :
        pass
    else :
      sha="sha384"
      hash_ = hashlib.sha384(message_bytes).digest()
    self.digest = {sha: hash_}

  #-------------------------------------------------------------------
  def func(self) :
    #self.requestsManager=RequestsManager(f'{self.args.crypto_key_id}')
    try :
      self.sign384(self.requestsManager.newRequest(self.keyparms["crypto_key_id"]),self.client,self.key_version_name,self.digest)
      if not self.response.name == self.key_version_name :
        raise Exception("The request sent to the server was corrupted in-transit.")
        print(f"Signature: {base64.b64encode(response.signature)!r}")
    except Exception as e :
      logging.error(f'{e}')
      self.runner.sendError(f'{e}')

  @Executor.exec
  #-------------------------------------------------------------------
  def sign384(self,client, name, digest):
    logging.info("invocated")
    self.response = client.asymmetric_sign( request={
              "name": name,
              "digest": digest,
        }
    )

