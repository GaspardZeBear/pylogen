import json
import sys

#------------------------------------------------------------------------------
#--- Defaults management, overiding by file
#------------------------------------------------------------------------------
class Defaults() :
  action="cuts.Dummy"
  id="customId"
  process="1"
  postpone="1"
  duration="5"
  loops="5"
  prefork="10"
  rampup="5"
  pauseloop="1"
  pausestep="1"
  summary="1"
  shmsize="1024"
  outformat="short"
  steps='A,256,512,1024,2048,4096,8192'
  extra='{}'

  @staticmethod
  def init(defaults="defaults.json") :
    #defaults="defaults.json"
    if "--defaults" in sys.argv :
      defaults=sys.argv[sys.argv.index("--defaults")+1]
    elif "--def" in sys.argv :
      defaults=sys.argv[sys.argv.index("--def")+1]
    print(f'defaults file : {defaults}')
    try :
      with open(defaults) as f :
        defs=json.loads(f.read())
        for k in defs.keys() :
          setattr(Defaults,k,defs[k])
    except Exception as e :
      print(f'{e} : using hardcoded defaults')

    print(f'{vars(Defaults)}')

