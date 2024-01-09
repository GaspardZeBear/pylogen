import logging
import json


def parseExtra(extraStr) :
  logging.info("starting parseExtra")
  extra=json.loads(extraStr)
  key=extra["key"]
  file="KmsDefault.json"
  if 'file' in extra :
    file=extra["file"]
  logging.info(f'ex+tra file : file={file}')
  with open(file) as fIn :
    keys=json.loads(fIn.read())
  keyparms=keys[key]
  return(keyparms)
