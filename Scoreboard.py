from multiprocessing.shared_memory import SharedMemory
import json
import time

class Scoreboard() :

  def __init__(self,id,shm) :
    self.shm = shm
    self.board={"id":id,"loopcount":0,"requests":{}}
    #print(f'shm={self.shm} {self.board}')

  def update(self,rmngr) :
    self.board["loopcount"] += 1
    #print(f'{rmngr}') 
    for r in rmngr.getRequests() :
      #print(f'{self.board["id"]} {r.getName()} {r.getRc()} {r.getDuration()}')
      if r.getName() not in self.board["requests"] :
        self.board["requests"][r.getName()]={
          "OK" : {"count":0,"durationSum":0,"durationAvg":0},
          "KO" : {"count":0,"durationSum":0,"durationAvg":0}
        }
      stats=self.board["requests"][r.getName()]["OK"]
      if r.getRc() != 0 :
        stats=self.board["requests"][r.getName()]["KO"]

      stats["count"] += 1
      stats["durationSum"] += r.getDuration()
      stats["durationAvg"] = stats["durationSum"]/stats["count"]


    self.publish()

  def publish(self) :
    #print(f'will publish shm={self.shm} {self.board}')
    boardAsBytes=json.dumps(self.board).encode('utf-8')
    boardLen=len(boardAsBytes).to_bytes(4,byteorder='big')
    self.shm.buf[0:4]=boardLen
    self.shm.buf[4:len(boardAsBytes)+4]=boardAsBytes

  def close(self) :
    print(f"close {self.shm}")
    self.shm.close()

  def unlink(self) :
    print(f"unlinking {self.shm}")
    self.shm.unlink()



