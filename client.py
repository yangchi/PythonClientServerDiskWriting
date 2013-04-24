#!/usr/bin/env python

import threading
import subprocess
import socket
import sys
import random
import os
import time

class Client():
    def __init__(self, endtime, chunksize, filesize, serveraddr, serverport):
        self.chunksize = int(chunksize)
        self.filesize = filesize
        self.serveraddr = serveraddr
        self.serverport = int(serverport)
        self.starttime = time.time()
        self.endtime = self.starttime + int(endtime)
    def run(self):
        routines = [self.sysinfo, self.heartbeat]
        for task in routines:
            thread = threading.Thread(target=task)
            thread.start()
        thread = threading.Timer(self.endtime - self.starttime, self.endclient)
        thread.start()
    def endclient(self):
        print "Time up. Bye bye!"
    def sysinfo(self):
        '''Get system info. Will also trigger a new thread to run after 10 seconds
        '''
        cpuinfo = subprocess.check_output(["grep", "model name", "/proc/cpuinfo"]).split("\n")
        cpuinfo.remove("")
        cpuinfo = ["CPU #"+str(index)+": "+cpu.replace('\t', '').replace(':','') for index, cpu in enumerate(cpuinfo)]
        cpureport = "\n".join(cpuinfo)
        meminfo = subprocess.check_output(["grep", "Mem", "/proc/meminfo"]).split("\n")
        meminfo.remove("")
        meminfo = [mem.replace('\t', '') for mem in meminfo]
        memreport = "MEM Info: " + ", ".join(meminfo)
        self.sendserver(cpureport+"\n"+memreport)
        if time.time() + 10 < self.endtime:
            thread = threading.Timer(10, self.sysinfo)
            thread.start()
    def heartbeat(self):
        '''Send out heartbeat every 5 secs
        '''
        self.sendserver("Heartbeat")
        if time.time() + 5 < self.endtime:
            thread = threading.Timer(5, self.heartbeat)
            thread.start()
    def filewriter(self):
        '''Write chunks to files
        '''
        random_chunk = os.urandom(self.chunksize)
    def sendserver(self, msg):
        '''Send infomation to server
        '''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.serveraddr, self.serverport))
        s.send(msg)
        s.close()


if __name__ == '__main__':
    myclient = Client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    myclient.run()
    #myclient.sysinfo()
    #myclient.filewriter()
