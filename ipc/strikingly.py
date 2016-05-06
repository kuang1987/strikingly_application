#!/usr/bin/env python

from mymmap import MyMmapObj
from time import sleep
import sys
import socket
import pickle

def ready(obj):
    print 'xiangxiang asked: %s'%obj['msg']
    return send_events[0]

def anwser(obj):
    print 'xiangxiang asked: %s'%obj['msg']
    return {'type':'QUES_ACK','msg':'got it!'}

def term(obj):
    'xiangxiang asked: %s'%obj['msg']
    return send_events[1]

def change(obj):
    'xiangxiang asked: change channel?'
    global port
    port = obj['port']
    return send_events[2]

port = 0
mm = None #communicate channel
sock = None
mmap_file = 'com.txt'
recv_events = [{'type':'READY','handler':ready},{'type':'TERM','handler':term},{'type':'QUES','handler':anwser},{'type':'CHANGE','handler':change}]
send_events = [{'type':'READY_ACK','msg':'I\'m ready'},{'type':'TERM_ACK','msg':'ok, please close'},{'type':'CHANGE_ACK','msg':'ok, wait for me set up!'}]
def eventListener(obj):
    type = obj['type']
    for events in recv_events:
        if events['type'] == type:
            return events['handler'](obj)

with open(mmap_file,'r+') as f:
    id=2
    accept_id = 1
    mm = MyMmapObj(id,accept_id,f)
    while 1:
        if mm.m_read():
            send_obj = eventListener(mm._coming_obj)
            print 'I answer: %s'%send_obj['msg']
            mm.m_write(send_obj)
            if send_obj['type'] == 'CHANGE_ACK':    
                break
        else:
            print 'I\'m waiting'
 
        sleep(2)

print "Changing Channel"  
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', port))   
sock.listen(1)   
while 1:   
    connection,address = sock.accept()
    connection.settimeout(50)  
 
    while 1:  
        buf = connection.recv(1024)
        if buf == '':
            break
        obj = pickle.loads(buf)
        send_obj = pickle.dumps(eventListener(obj))
        print 'I answer: %s'%obj['msg']
        connection.send(send_obj)
        if obj['type'] == 'TERM_ACK': 
            break
    connection.close()
    break 

