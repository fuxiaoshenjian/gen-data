from snowFlake import IdGenerator
from kafka import KafkaProducer
import multiprocessing
import copy
import threading
import time
import sys
import copy
import random
import string 

"""for calculating processes"""
q = multiprocessing.Queue(10)
"""for loading conf"""
params = {}
#producer = KafkaProducer(bootstrap_servers=['172.16.3.79:9092','172.16.3.80:9092','172.16.3.81:9092']) 

def enum(**enums):
    return type('Enum', (), enums)

 
types = enum(no='no', string='string', int='int', float='float', date='date') #id:self incr int


class Singleton(object):
    __instance=None
    def __init__(self):
	pass
    def __new__(cls,*args,**kwd):
	if Singleton.__instance is None:
	    Singleton.__instance=object.__new__(cls,*args,**kwd)
	    return Singleton.__instance


class ConfLoader(Singleton):
    """loading conf from argv or conf file"""
    seq = []
    def __init__(self):
	pass

    def loadConf(self, conf=""):
	"""NO CONSTRAIN,TODO"""
	arg = sys.argv[1]
	self.seq=[]
	count = 0
        global params	
        params['filename'] = sys.argv[3] if len(sys.argv) > 3 else "data.csv"	
        params['processnum'] = int(sys.argv[4]) if len(sys.argv) > 4 else 50
        params['rownum'] = int(sys.argv[2])/params['processnum'] if len(sys.argv) > 2  else 10000	
	
	for i in arg:
	    if i == 't':
		self.seq.append(["t"])
	    if i == 'i':
		try:
		    c = int(arg[count+1])
                    self.seq.append(['int', c])
		except:
                    self.seq.append(['int'])
	    elif i == 'n':
	        self.seq.append(['no'])
	    elif i == 'f':
		self.seq.append(['float'])
	    elif i == 's':
                try:
                    c = int(arg[count+1])
                    self.seq.append(['string', c])
		except:
		    self.seq.append(['string'])
	    elif i == 'd':
		self.seq.append(['date'])
	    count += 1
	return self.seq


class itemFactory(object):
    """generate a certain type token"""
    incr = 0
    def INCR(self):
        self.incr += 1
        return self.incr

    def randInt(self,n=4):
	return random.randint(0, 10**n)

    def randFloat(self):
	#TODO
	pass

    def randStr(self,n=3):
	x = ""
        for i in range(random.randint(3,2**n)):
	    x += random.choice(string.ascii_lowercase)
	return x

    def randDate(self):
	now = time.time()
	t = random.randint(int(now-86400*2000), int(now))
	tnow = time.localtime(float(t))
        return time.strftime('%Y-%m-%d %H:%M:%S',tnow)	

    def productItem(self,type,range=4):
        if type == types.int:
	    return self.randInt(range)
	elif type == types.string:
	    return self.randStr(range)   
	elif type == types.float:
	    return self.randFloat()	    
	elif type == types.date:
	    return self.randDate()
	elif type == types.no:
	    return self.INCR()	
	elif type == 't':
	    return "t"


class dataFactory(multiprocessing.Process):
    """Generate&Write for multitypes output """
    def __init__(self, processname, useKafka=False,conf=None):
	"""args: \ 
	useKafka:output to kafka, Call initKafka method needed \
	conf:A ConfLoader instance
	"""
	global params
        multiprocessing.Process.__init__(self,name=processname) 
	self.kafka = useKafka
	self.seq = conf.loadConf()
	self.separator = ','
	self.filename = params['filename'] + processname
	self.file = open(self.filename, 'a')

    def setSeparator(x):
	self.separator = x

    def productLine(self, a=0):
	"""Build a line \
	Callback function"""
        f = itemFactory()
	line=""
	for i in self.seq:
	    if i[0] == 'no':
		line += str(a)
	    else:
		line += str(f.productItem(*i))
	    line += self.separator
	line = line[:-1]+'\n'
	return line 

    def lambdas(self):
	"""Put productLine to GenId 
	as a param, Generator"""
	l = self.productLine()	
	g = IdGenerator()
	return g.GenId(self.productLine)
	
    def initKafka(self, boot_server):
	self.bs = boot_server
        self.producer = KafkaProducer(bootstrap_servers = boot_server) 
	#self.producer = copy.deepcopy(producer)

    def massProduct(self, args):
        pass

    def Write(self):
	"""Almost abandoned, rows generator"""
	i = 0
	global params
	n = params['rownum']
	x = self.lambdas()
	while i != n:
	    i += 1
	    l = x.next()
	    yield l
    
    def run(self):
	"""thread call, port"""
	global q
	q.put(1)
	t = time.time()
	w = self.Write()
        #producer = copy.deepcopy(self.producer)
	producer = KafkaProducer(bootstrap_servers=['172.16.3.79:9092','172.16.3.80:9092','172.16.3.81:9092']) 
	#producer = KafkaProducer(bootstrap_servers = self.bs)
	try:
	    package = ""
	    count = 0
	    while True:
		count += 1
		if self.kafka == True:
		    package += w.next()
		    if count % 10000 == 0:
		        producer.send('factory2', package)
			package = ""
		    print package
		else:
		    l = w.next()
		    print w.next().strip()
	except StopIteration:
	    
	    q.get()


if __name__ == '__main__':
    t = time.time()
    b_server = ['172.16.3.79:9092','172.16.3.80:9092','172.16.3.81:9092']
    #producer = KafkaProducer(bootstrap_servers=['172.16.3.79:9092','172.16.3.80:9092','172.16.3.81:9092']) 
    pn = int(sys.argv[4])
    conf = ConfLoader()
    for i in range(pn):
        df = dataFactory("", True, conf)
	df.initKafka(b_server)
        df.start()
