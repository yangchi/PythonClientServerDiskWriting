#!/usr/bin/env python

import select
import threading
import socket
import time
import re
import sqlite3
import os.path


class Server():
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.lock = threading.Lock()
        self.report_f = open("server_report-" + time.ctime().replace(' ', '_') + ".out", "w")
        self.report_f.write("Server starts at: " + time.ctime() + "\n")
        self.report_f.flush()
        self.logging("Server starts at: " + time.ctime())
        self.clients = set()
        self.cpustats = {}
        self.vmsize_stats = {}
        self.vmrss_stats = {}
        if not os.path.isfile("server.db"):
            conn = sqlite3.connect("server.db")
            cs = conn.cursor()
            cs.execute("CREATE TABLE clients (host text, port integer, time text, CPU real, VmSize integer, VmRSS integer)")
            conn.commit()
            conn.close()
        self.establish()

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
            try:
                r_ready, w_ready, err_ready = select.select([s], [], [], 60)
                if not r_ready:
                    print "No new client come in the past 60 seconds. Quit"
                    break
                for s_ready in r_ready:
                    if s_ready is s:
                        conn, addr = s.accept()
                        print "Connetion from", addr
                        self.logging("Connection from " + str(addr))
                        loginfo = "Total thread now: " + str(len(threading.enumerate()))
                        self.logging(loginfo)
                        print loginfo
                        thread = threading.Thread(target=self.client_handler, args=(conn, addr))
                        thread.start()
                    else:
                        #other socket, I'm going to ignore them for now
                        pass
            except KeyboardInterrupt:
                print "\nCtrl+C pressed. Leaving loop"
                break

        while len(threading.enumerate()) > 1:
            pass
        self.report()
        print "Nice serving all the clients. Bye bye."

    def report(self):
        self.report_f.write("Total number of served clients: " + str(len(self.clients)) + "\n")
        for client in self.clients:
            self.report_f.write("======================================\n" +
                                "Perf stat of client " + client + ":\n")
            self.report_f.write("\t Average CPU Usage: " +
                                str(float(sum(self.cpustats[client])) / len(self.cpustats[client]) if len(self.cpustats[client]) > 0 else float('nan')) +
                                "\n")
            self.report_f.write("\t Average virtual memory size: " +
                                str(float(sum(self.vmsize_stats[client])) / len(self.vmsize_stats[client]) if len(self.vmsize_stats[client]) > 0 else float('nan')) +
                                "\n")
            self.report_f.write("\t Average virtual memory resident set size: " +
                                str(float(sum(self.vmrss_stats[client])) / len(self.vmrss_stats[client]) if len(self.vmrss_stats[client]) > 0 else float('nan')) +
                                "\n")
        self.report_f.close()

    def client_stats(self, (host, port, cpu, vmsize, vmrss)):
        client = host + ":" + port
        self.clients.add(client)
        if client in self.cpustats:
            self.cpustats[client].append(float(cpu))
        else:
            self.cpustats[client] = [float(cpu)]
        if client in self.vmsize_stats:
            self.vmsize_stats[client].append(float(vmsize))
        else:
            self.vmsize_stats[client] = [float(vmsize)]
        if client in self.vmrss_stats:
            self.vmrss_stats[client].append(float(vmrss))
        else:
            self.vmrss_stats[client] = [float(vmrss)]

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
            conn = sqlite3.connect("server.db")
            cs = conn.cursor()
            cs.execute("INSERT INTO clients VALUES (?,?,?,?,?,?)", [host, port, time.ctime(), cpu, vmsize, vmrss])
            conn.commit()
            conn.close()
            self.client_stats((host, port, cpu, vmsize, vmrss))

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
