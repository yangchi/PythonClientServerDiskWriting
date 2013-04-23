#!/usr/bin/env python

import threading
import subprocess
import socket

class Client():
    def __init__(self, chunksize, filesize, serveraddr, serverport):
        self.chunksize = chunksize
        self.filesize = filesize
        self.serveraddr = serveraddr
        self.serverport = serverport
    def run(self):
        routines = [self.sysinfo, self.heartbeat]
        for task in routines:
            thread = threading.Thread(target=task)
            thread.start()
    def sysinfo(self):
        cpuinfo = subprocess.check_output(["grep", "model name", "/proc/cpuinfo"])
        meminfo = subprocess.check_output(["grep", "Mem", "/proc/meminfo"])
        self.sendserver(cpuinfo+"\n"+meminfo)
        thread = threading.Timer(10, self.sysinfo)
        thread.start()
    def heartbeat(self):
        thread = threading.Timer(5, self.heartbeat)
        thread.start()
    def sendserver(self, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.serveraddr, self.serverport))
        s.send(socket.htons(msg))
        s.close()


if __name__ == '__main__':
    myclient = Client(10, 10, "127.0.0.1", 1234)
    myclient.run()
