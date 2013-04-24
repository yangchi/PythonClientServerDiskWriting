#!/usr/bin/env python

import threading
import socket
import time
import re


class Server():
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.lock = threading.Lock()
        self.logging("Server starts")

    def logging(self, msg):
        with self.lock:
            self.logfile = open("server.log", "a")
            self.logfile.write(time.ctime() + ": " + msg + "\n")
            self.logfile.close()

    def establish(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.addr, self.port))
        s.listen(10)
        print "============= Server Info Begin ============="
        loginfo = "listening at [" + self.addr + "(" + socket.gethostbyname(self.addr) + "): " + str(self.port) + "]"
        self.logging(loginfo)
        print loginfo
        print "============= Server Info End ==============="
        while True:
            conn, addr = s.accept()
            print "Connetion from", addr
            self.logging("Connection from " + str(addr))
            loginfo = "Total thread now: " + str(len(threading.enumerate()))
            self.logging(loginfo)
            thread = threading.Thread(target=self.client_handler, args=(conn, addr))
            thread.start()

    def extract_perf(self, msg):
        msg = msg.replace('\n', '')
        pattern = "^System info from.*\[(?P<Host>.*):\s+(?P<port>\d+)\]:.*\s+CPU Usage:\s+(?P<cpu>\d+\.\d*).*VmSize:\s+(?P<VmSize>\d+).*VmRSS:\s+(?P<VmRSS>\d+).*"
        regex = re.compile(pattern)
        m = regex.search(msg)
        if m:
            host = m.group('Host')
            port = m.group('port')
            cpu = m.group('cpu')
            vmsize = m.group('VmSize')
            vmrss = m.group('VmRSS')

    def client_handler(self, conn, addr):
        received = conn.recv(1024)
        while received:
            received = conn.recv(1024)
            if received:
                if "System" in received:
                    self.extract_perf(received)
                self.logging(received)
        conn.close()
        print "Connection to " + str(addr) + " closed"
        self.logging("Connection to " + str(addr) + " closed.")

if __name__ == '__main__':
    myserver = Server(socket.gethostname(), 1234)
    myserver.establish()
