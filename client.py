#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import threading
from serie import serie
import socket
import struct
import json
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
        self.dowork = True
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
                print("--")
                self.connectToTCPServer(str(sender[0]))
                print("--")
            else:
                print("Already connected to server")
        print("Done listening to MC")


    def connectToTCPServer(self, address_to_connect):
        try:
            self.connected = True
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            addr = socket.getaddrinfo(address_to_connect, self.MYPORT - 10, socket.AF_INET6, 0, socket.SOL_TCP)[0]
            sock.connect(addr[-1])
            print("Unicast connection with server stablished")
            self.unicast_connected_to = sock
            new_con = threading.Thread(name='server', target=self.tcpConnectedTo, args=[sock])
            new_con.start()
            new_con.join(1)
            self.receive_multicast_info = False
        except Exception as e:
            self.connected = False
            print(e, file=sys.stderr)
            print("Error: Perhaps server is not listening :(")

    def tcpConnectedTo(self, server):
        try:
            while self.dowork:
                data = server.recv(1024).decode()
                if len(data):
                    print('Received from server: ', data)
                    self.checkData(data)
        except Exception as e:
            print(e)
            print("Error")
        server.close()

    def checkData(self, data):
        try:
            data = json.loads(data)
            if data["type"] == "process":
                s = serie()
                r = s.calc((int(data["initial"]), int(data["final"])))
                print("Calculated "+str(r[0][0]))
                print("Complete interval "+str(r[0][1]))
                print("Time "+str(r[1]))
                info_to_send = json.dumps({"initial": data["initial"], "final": data["final"], "type": "response", "interval": r[0][1], "time": r[1]})
                try:
                    self.sendToServer(self.unicast_connected_to, info_to_send)
                except Exception as e:
                    print(e)
                    print("Error: server is no longer listening")
        except Exception as e:
            print("No json")


    def sendToServer(self, server, data):
        print ('Sending to server :', data)
        server.send(data.encode())



if __name__ == "__main__":
    try:
	    s = client()
    except Exception as e:
        print(e)
        print("Usage: client.py")
