#!/usr/bin/env python

from mymmap import MyMmapObj
from time import sleep
import sys
import socket
import pickle

question_index = 0
mmap_file = './com.txt'
mm = None #communicate channel
channel_changed = False
port = 3000
def eventListener(obj):
    type = obj['type']
    for events in recv_events:
        if events['type'] == type:
            return events['handler'](obj)

def send_question(obj):
    print 'strikingly anwsered: %s'%obj['msg']
    global question_index,channel_changed
    if question_index < len(question_list):
        send_obj = {'type':'QUES','msg':question_list[question_index]}
        if question_index == 1 and (not channel_changed):
            print 'I ask: change Channel?'
            send_obj = send_events[2]
            question_index -= 1
    else:
        send_obj = send_events[1]
 
    question_index += 1

    return send_obj

def exit(obj):
    print 'strikingly anwsered: %s'%obj['msg']
    global sock
    if sock:
        sock.close()
    return None

def change(obj):
    print 'strikingly anwsered: %s'%obj['msg']
    global channel_changed
    channel_changed = True
    return None

send_events = [{'type':'READY','msg':'are you ready?'},{'type':'TERM','msg':'I will close!'},{'type':'CHANGE','port':port}]
recv_events = [{'type':'READY_ACK','handler':send_question},{'type':'QUES_ACK','handler':send_question},{'type':'TERM_ACK','handler':exit},{'type':'CHANGE_ACK','handler':change}]
question_list = ['what\'s the strikingly like in your mind?',
                'Can employees have chance to work abroad?',
                'what\'s the revenune situation now?',
                'what\'s the plan in next few years including team expansion, produce, IPO and etc?',
                'Will the company try a different business field?']


with open(mmap_file,'w') as f:
    f.write('a'*1024*1024)

with open(mmap_file,'r+') as f:
    id=1
    accept_id = 2
    mm = MyMmapObj(id,accept_id,f)
    #start interaction
    mm.m_write(send_events[0])
    while 1:
        if mm.m_read():
            send_obj = eventListener(mm._coming_obj)
            if channel_changed:
                mm.m_close()
                break
            mm.m_write(send_obj)
        else:
            sleep(2)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while 1:
    print 'try to changing to new channel'
    try:
        sock.connect(('localhost', port))
        break
    except:
        sleep(2)


sock.send(pickle.dumps(send_events[0]))
while 1:
    buf = sock.recv(1024)
    if buf:
        obj = pickle.loads(buf)
        send_obj = eventListener(obj)
        if send_obj:
            print 'I ask: %s'%send_obj['msg']
        else:
            break
        sleep(2)
        sock.send(pickle.dumps(send_obj))
    
