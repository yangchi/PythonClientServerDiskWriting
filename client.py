#!/usr/bin/env python

import subprocess
import threading
import socket
import sys
import os
import time


class Client():
    def __init__(self, endtime, chunksize, filesize, serveraddr, serverport):
        ''' Client constructor
        arguments:
            endtime --- total running time in secs
            chunksize --- size of each "chunk"
            filesize --- size of each "file"
            serveraddr --- IP address or hostname of the server
            serverport --- server port
        '''
        (self.utime, self.stime, NULL, NULL, self.etime) = os.times()
        self.chunksize = int(chunksize)
        self.filesize = int(filesize)
        self.serveraddr = serveraddr
        self.serverport = int(serverport)
        self.starttime = time.time()
        self.endtime = self.starttime + int(endtime)
        self.cpuusage = 0
        self.start_conn()
        self.identity = "[" + socket.gethostname() + \
                        "(" + socket.gethostbyname(socket.gethostname()) + "): " + \
                        str(self.sock.getsockname()[1]) + "]"
        loginfo = time.ctime() + ": Client at " + self.identity + " starts."
        self.logging(loginfo)
        self.sendserver(loginfo)
        self.wrtfile = True
        self.allowend = False
        self.run()

    def logging(self, msg):
        self.logfile = open("client.log", "a")
        self.logfile.write(msg + "\n")
        self.logfile.close()

    def run(self):
        ''' Start the threads
        '''
        routines = [self.sysinfo, self.heartbeat]
        for task in routines:
            thread = threading.Thread(target=task)
            thread.start()
        thread = threading.Timer(self.endtime - self.starttime, self.endclient)
        thread.start()
        thread = threading.Thread(target=self.filewriter)
        thread.start()

    def endclient(self):
        self.wrtfile = False
        while not self.allowend:
            pass
        print "Time up. Bye bye!"
        loginfo = time.ctime() + ": Client at " + self.identity + " stops."
        self.logging(loginfo)
        self.sendserver(loginfo)
        self.sock.close()

    def timestats(self):
        ''' Collect cpu times and calculate the CPU usage
        '''
        (utime, stime, NULL, NULL, etime) = os.times()
        while etime == self.etime:
            (utime, stime, NULL, NULL, etime) = os.times()
        self.cpuusage = (utime - self.utime + stime - self.stime) / (etime - self.etime) * 100
        self.utime = utime
        self.stime = stime
        self.etime = etime
        return self.cpuusage

    def sysinfo(self):
        '''Get system info. Will also trigger a new thread to run after 10 seconds
        '''
        cpureport = "\tCPU Usage: " + str(self.timestats()) + "%"
        statusfile = "/proc/%d/status" % os.getpid()
        meminfo = subprocess.check_output(["grep", "Vm", statusfile]).split("\n")
        meminfo.remove("")
        meminfo = [mem.replace('\t', ' ') for mem in meminfo if "RSS" in mem or "Size" in mem]
        memreport = "\tMEM Usage: " + "\t".join(meminfo)
        self.sendserver("System info from " + self.identity + ":\n" + cpureport + "\n" + memreport)
        if time.time() + 10 < self.endtime:
            thread = threading.Timer(10, self.sysinfo)
            thread.start()

    def heartbeat(self):
        '''Send out heartbeat every 5 secs
        '''
        self.sendserver("Heartbeat from " + self.identity)
        if time.time() + 5 < self.endtime:
            thread = threading.Timer(5, self.heartbeat)
            thread.start()

    def filewriter(self):
        '''Write chunks to files
        '''
        counter = 0
        while self.wrtfile:
            counter += 1
            filename = "Client-output-" + time.ctime().replace(' ', '_').replace(':', '-')
            f = open(filename, 'w')
            leftsize = self.filesize
            while leftsize > self.chunksize:
                random_chunk = os.urandom(self.chunksize)
                f.write(random_chunk)
                leftsize -= self.chunksize
            if leftsize:
                random_chunk = os.urandom(leftsize)
                f.write(random_chunk)
            f.close()
            loginfo = time.ctime() + ": file " + filename + " rollover!"
            self.logging(loginfo)
            self.sendserver(loginfo)
        self.allowend = True

    def sendserver(self, msg):
        '''Send infomation to server
        '''
        self.sock.send(msg)

    def start_conn(self):
        ''' Connect to server
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.serveraddr, self.serverport))


if __name__ == '__main__':
    myclient = Client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
