#!/usr/bin/env python

import socket

class Server():
    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
    def establish(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.addr, self.port))
        s.listen(10)
        while True:
            conn, addr = s.accept()
            received = conn.recv(1024)
            print received

if __name__ == '__main__':
    myserver = Server("127.0.0.1", 1234)
    myserver.establish()
