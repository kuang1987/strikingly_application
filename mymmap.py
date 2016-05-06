#!/usr/bin/env python

import mmap
import pickle

print mmap.mmap

class MyMmapObj:
    def __init__(self,id,accept_id,f,length=0,flags=mmap.MAP_SHARED,prot=mmap.PROT_READ|mmap.PROT_WRITE,access=mmap.ACCESS_WRITE):
        #super(MyMmapObj,self).__init__(self,f.fileno(),0)
        self.mm = mmap.mmap(f.fileno(),0,access=access)
        self._id = id
        self._accept_id = accept_id
        
    def m_write(self,obj):
        try:
            #print 'sent ' + str(obj)
            self.str = pickle.dumps(obj,0)
            self.content_length = len(self.str) 
            self.content = hex(self._id)[2:].zfill(4) + hex(self.content_length)[2:].zfill(4) + self.str
            self.mm.seek(0)
            self.mm.write(self.content)
            self.mm.flush()
            return True 
        except Exception,e:
            print str(e)
            return False


    def m_read(self):
        try:
            self.mm.seek(0)
            self._coming_id = int(self.mm.read(4),16)
            if self._coming_id != self._accept_id:
                return False
            self._coming_content_length = int(self.mm.read(4),16)
            self._coming_obj = pickle.loads(self.mm.read(self._coming_content_length))
            return True
        except Exception,e:
            print str(e)
            return False

    def m_close(self):
        self.mm.close()


if __name__ == '__main__':
    mmap_file = 'com.txt'

    with open(mmap_file,'wb') as f:
        f.write('a'*1024*1024)

    with open(mmap_file,'r+b') as f:
        id=1
        mm = MyMmapObj(id,f.fileno())

        send_events = [{type:'READY',msg:'are you ready?'}]

        while 1:
            if mm.m_write(send_events[0]):
                print 'send success'
            sleep(2)
