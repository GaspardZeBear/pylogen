from multiprocessing.shared_memory import SharedMemory
import json
import time

class Scoreboard() :

  def __init__(self,id,shm) :
    self.shm = shm
    self.board={"id":id,"loopcount":0}
    #print(f'shm={self.shm} {self.board}')

  def update(self) :
    self.board["loopcount"] += 1

  def publish(self) :
    #print(f'will publish shm={self.shm} {self.board}')
    boardAsBytes=json.dumps(self.board).encode('utf-8')
    boardLen=len(boardAsBytes).to_bytes(4,byteorder='big')
    self.shm.buf[0:4]=boardLen
    self.shm.buf[4:len(boardAsBytes)+4]=boardAsBytes
    #self.shm.close()


