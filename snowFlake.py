"""Generate unique key in high concurrence environment \
Use snowflake algorithm"""
import time
import random
import os

def format(id, length=5):
    """encode id to snowflake format"""
    return str(bin(id))[2:] if len(str(int(id))[2:])>4 else (5-len(str(bin(id))[2:]))*"0"+str(bin(id))[2:]


class IdGenerator(object):
    """Generator unique Key in distribute system, \
    Thread safe, multiprocessing safe"""
    def __init__(self):
        self.mid = int(os.popen("hostname").read()[3:].strip())
	self.pid = random.randint(0,256)

    def GenerateTime(self):
         """mili timestamp, 41 bits"""
         return str(bin(int(round(time.time() * 1000))))[2:]
    
    def GenDistinctId(self):
	"""generate machine id and process id, join them together"""	
        """4 bits to unique a machine \
	5 bits for processes"""
	machineId = format(self.mid, 4)
        processId = format(self.pid) 
    	return machineId + processId
	
    def GenId(self, func=None, *param):
	"""Completely gen an Id \
	TODO:CALLBACK FUNCTION F;YIELD F(ID)"""
	current_count = 0
	old_time = self.GenerateTime()
	while True:	
	    current_count += 1
	    if self.GenerateTime() != old_time:
		current_count = 0
	    old_time = self.GenerateTime()
	    CurrentId = format(current_count, 11)
	    #id = str(int(self.GenerateTime(), 2) + int(self.GenDistinctId(), 2) + int(CurrentId, 2))
	    id = str(int(self.GenerateTime(), 2)) + str(int(self.GenDistinctId(), 2)) + str(int(CurrentId, 2))
	    yield(func(id, *param))		


class cc():
    def cat(self, a,b="aaa", c="fff"):
        return a
    
if __name__ == "__main__":
     g = IdGenerator()
     w = g.GenId(cc().cat)
     while w.next():
	print w.next()
