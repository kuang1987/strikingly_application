import os,sys
import signal
from time import sleep

pid_file = __file__ + '.pid'

if os.path.exists(pid_file):
    with open(pid_file,'r') as f:
        pid = f.readlines()
    print 'one process running with pid %s, I will exit'%pid[0]
    sys.exit(-1)
else:
    with open(pid_file,'w') as f:
        f.write(str(os.getpid()))

def onsignal_term(a,b):
    delete_pid_file()
    print 'SIGTERM RECEIVED'
    sys.exit(0)

signal.signal(signal.SIGTERM,onsignal_term)

def onsignal_int(a,b):
    delete_pid_file()
    print 'SIGINT RECEIVED'
    sys.exit(0)

signal.signal(signal.SIGINT,onsignal_term)

def delete_pid_file():
    os.remove(pid_file)

while 1:
    print 'I\'m running'
    sleep(2)
