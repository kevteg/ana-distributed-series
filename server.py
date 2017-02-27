#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import threading
import serie
import socket
from comunication import getConnectionInfo, createMulticastSocket, getOwnLinkLocal
class server:
    def __init__(self, number, connection_time = 10):
        os.system("clear")
        self.number = number
        self.connection_time = connection_time
        self.sendinfo = True
        self.dowork = True
        self.unicast_connections = []
        group, self.MYPORT = getConnectionInfo("distributed")
        self.multicast_sock, self.addrinfo, self.interface = createMulticastSocket(group, self.MYPORT)
        send_information = threading.Thread( name='send_information', target=self.send_information)
        wait_connection = threading.Thread( name='wait_connection', target=self.wait_connection)
        tcp_thread = threading.Thread( name='tcp_thread', target=self.waitTCPCLients, args=[self.interface])
        tcp_thread.start()
        wait_connection.start()
        send_information.start()
        tcp_thread.join(1)
        wait_connection.join(1)
        send_information.join(1)

    def divide_work(self):
        pass

    def send_information(self):
        while self.sendinfo:
            time.sleep(0.5)
            print("\033[3;0H")
            self.sendToGroup("Hi")
        print("\033[3;0H")
        print("Multicast: Sent finished                       ")

    def waitTCPCLients(self, interface):
        addr = socket.getaddrinfo(getOwnLinkLocal(interface) + '%' + interface, self.MYPORT - 10, socket.AF_INET6, 0, socket.SOL_TCP)[0]
        self.tcp_socket = socket.socket(addr[0], socket.SOCK_STREAM)
        self.tcp_socket.bind(addr[-1])
        self.tcp_socket.listen(10)
        print("\033[4;0H")
        print ("Waiting for TCP connections, address: '%s'" % str(addr[-1][0]))
        try:
            while self.dowork:
                conn, address = self.tcp_socket.accept()
                print("\033[4;0H")
                print("Connection stablished with " + str(address))
                self.unicast_connections.append(threading.Thread(name='tcpConnection', target=self.tcpConnection, args=[conn]))
                self.unicast_connections[-1].start()
                self.unicast_connections[-1].join(1)
        except (KeyboardInterrupt, SystemExit):
            self.tcp_socket.close()
            self.dowork = False
        self.tcp_socket.close()

    def tcpConnection(self, client):
        try:
            while self.dowork:
                data = client.recv(1024).decode().rstrip('\0').lstrip('\0')
                print('Received from one client:', repr(data))
        except Exception as e:
            print(e)
            self.tcp_socket.close()
            self.dowork = False
        client.close()

    def wait_connection(self):
        for i in range(1, int(self.connection_time) + 1):
            time.sleep(1)
            print("\033[2;0H")
            print("Ana's serie: Beginning in " + str(i))
        print("\033[2;0H")
        print("Ana's serie: Information will be sent to clients now!")
        self.sendinfo = False

    def sendToGroup(self, message):
        print("Multicast: Sending: " + message)
        self.multicast_sock.sendto(message.encode(), (self.addrinfo[4][0], self.MYPORT))

if __name__ == "__main__":
    try:
	    s = server(sys.argv[1], (sys.argv[2] if len(sys.argv) >= 3 else 10))
    except Exception as e:
        print(e)
        print("Usage: server.py number time-to-begin")
