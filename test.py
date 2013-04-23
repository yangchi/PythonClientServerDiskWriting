#!/usr/bin/env python

import threading
import subprocess

class Client():
    def __init__(self):
        print "Client started"
        self.threads = []
    def run(self):
        tasks = [self.cpuinfo, self.meminfo]
        for task in tasks:
            thread = threading.Thread(target=task)
            thread.start()
    def cpuinfo(self):
        cpuinfo = subprocess.check_output(["grep", "model name", "/proc/cpuinfo"])
        print cpuinfo
        #thread = threading.Timer(3, self.cpuinfo)
        #thread.start()
        return cpuinfo
    def meminfo(self):
        meminfo = subprocess.check_output(["grep", "Mem", "/proc/meminfo"])
        print meminfo
        return meminfo

if __name__ == '__main__':
    myclient = Client()
    myclient.run()
    #myclient.cpuinfo()
    #myclient.meminfo()
