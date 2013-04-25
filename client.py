#!/usr/bin/env python

import subprocess
import threading
import socket
import sys
import os
import time
import random


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
        #if int(chunksize) < int(filesize) * 2:
        #    print "Error!! \n Chunk size should be at least twice as large as file size. Quit"
        #    sys.exit(1)
        self.chunksize = int(chunksize)
        self.filesize = int(filesize)
        if not self.timelimit_checker(int(endtime)):
            sys.exit(1)
        self.serveraddr = serveraddr
        self.serverport = int(serverport)
        self.starttime = time.time()
        self.endtime = self.starttime + int(endtime)
        self.cpuusage = 0
        self.start_conn()
        self.identity = "[" + socket.gethostname() + \
                        "(" + socket.gethostbyname(socket.gethostname()) + "): " + \
                        str(self.sock.getsockname()[1]) + "]"
        loginfo = time.ctime() + ": Client at " + self.identity + \
                                 " starts with configuration: chunk size = " + \
                                 str(self.chunksize) + " file size = " + str(self.filesize)
        self.logging(loginfo)
        self.sock.send(loginfo)
        self.wrtfile = True
        self.allowend = False
        self.run()

    def speedtest(self):
        tempf = open("temp", "w")
        data = os.urandom(1000 * 1000)
        first = time.time()
        tempf.write(data)
        tempf.close()
        second = time.time()
        speed = 1000.0 * 1000.0 / (second - first) if second > first else float('inf')
        os.remove("temp")
        return speed

    def timelimit_checker(self, timelimit):
        speed = self.speedtest()
        if self.filesize * 2 > speed * timelimit:
            print "Error!! \n The length of time configured is not enough for at least 2 file rollovers based on our estimated file io speed. Quit"
            return False
        else:
            return True

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
        self.sock.send(loginfo)
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
        self.sock.send("System info from " + self.identity + ":\n" + cpureport + "\n" + memreport)
        if time.time() + 10 < self.endtime:
            thread = threading.Timer(10, self.sysinfo)
            thread.start()

    def heartbeat(self):
        '''Send out heartbeat every 5 secs
        '''
        self.sock.send("Heartbeat from " + self.identity)
        if time.time() + 5 < self.endtime:
            thread = threading.Timer(5, self.heartbeat)
            thread.start()

    def chunkwriter(self):
        '''In this one we assume chunks are larger than files
            this assumption was wrong.
        '''
        the_chunk = os.urandom(self.chunksize)
        pos = 0
        counter = 0
        while pos < self.chunksize:
            counter += 1
            filename = "Client-output-" + self.identity + "-" + time.ctime().replace(' ', '_').replace(':', '-') + "-" + str(counter)
            f = open(filename, 'w')
            endpos = pos + self.filesize if self.chunksize > pos + self.filesize else self.chunksize
            f.write(the_chunk[pos:endpos])
            f.close()
            pos += self.filesize
            loginfo = time.ctime() + ": file " + filename + " rollover! at " + self.identity
            self.logging(loginfo)
            self.sock.send(loginfo)
        self.allowend = True

    def filewriter(self):
        '''Write chunk to files.
            Diff from self.chunkwriter, in this function we assume chunks are smaller than files.
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
            loginfo = time.ctime() + ": file " + filename + " rollover! at " + self.identity
            self.logging(loginfo)
            self.sock.send(loginfo)
        self.allowend = True

    def start_conn(self):
        ''' Connect to server
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((self.serveraddr, self.serverport))
        except Exception:
            print >> sys.stderr, "Not able to connect to the server"
            self.logging("Connection to " + self.serveraddr + ": " + str(self.serverport) + " fails.")
            self.logging(time.ctime() + ": Client stops.")
            sys.exit(1)


if __name__ == '__main__':
    #myclient = Client(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    if len(sys.argv) < 3:
        print >> sys.stderr, "Please use 'client.py server server-port'"
        sys.exit(1)
    for i in range(5):
        client = Client(random.randint(10, 25), random.randint(1000, 9000), random.randint(1000000, 2000000), sys.argv[1], sys.argv[2])
