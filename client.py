#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import threading
import serie
import socket
import struct
from comunication import getConnectionInfo, createMulticastSocket
class client:
    def __init__(self):
        os.system("clear")
        self.receive_multicast_info = True
        group, self.MYPORT = getConnectionInfo("distributed")
        self.multicast_sock, self.addrinfo, self.interface = createMulticastSocket(group, self.MYPORT)
        self.multicast_sock.bind(('', self.MYPORT))
        self.unicast_connected_to = None
        self.connected = False
        self.dowork = False
        # self.multicast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        receive_information = threading.Thread( name='receive_information', target=self.receive_information)
        receive_information.start()
        receive_information.join(1)

    def receive_information(self):
        while self.receive_multicast_info:
            data, sender = self.multicast_sock.recvfrom(1500)
            while data[-1:] == '\0': data = data[:-1] # Strip trailing \0's
            print(str(sender[0]) + ' ' + str(data))
            if not self.connected:
                self.connectToTCPServer(str(sender[0]))
            else:
                print("Already connected to server")


    def connectToTCPServer(self, address_to_connect):
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            addr = socket.getaddrinfo(address_to_connect, self.MYPORT - 10, socket.AF_INET6, 0, socket.SOL_TCP)[0]
            sock.connect(addr[-1])
            self.connected = True
            print("Unicast connection with server")
            self.unicast_connected_to = (threading.Thread(name='server', target=self.tcpConnectedTo, args=[sock]))
            self.unicast_connected_to.start()
        except Exception as e:
            print(e, file=sys.stderr)
            print("Server seems to not be listening :(")

    def tcpConnectedTo(self, server):
        try:
            # self.sendToServer(server, "HOLA VALE")
            while self.dowork:
                data = server.recv(1024)
                print('Received from server:', repr(data))
        except Exception as e:
            print(e)
            print("Error")

    def sendToServer(self, server, data):
        print ('Sending to server :', repr(data))
        # _s = int(1024 - len(data.encode()))
        # data = (struct.pack(str(_s) + 'B',*([0]*_s))).decode() + data
        server.send(data.encode())



if __name__ == "__main__":
    try:
	    s = client()
    except Exception as e:
        print(e)
        print("Usage: client.py")
