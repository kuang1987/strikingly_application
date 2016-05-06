import os
import signal
from time import sleep

count = 20

def onsignal_term(a,b):
    print 'SIGTERM RECEIVED'
    global i
    if i < count:
        print 'I\'m not finished'

signal.signal(signal.SIGTERM,onsignal_term)

i = 0
while i < count:
    print 'My pid is',os.getpid()
    i = i + 1
    sleep(10)
