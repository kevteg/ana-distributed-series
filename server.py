#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import threading
from serie import serie
import socket
import struct
import select
import json
from collections import OrderedDict
from math import ceil
from comunication import getConnectionInfo, createMulticastSocket, getOwnLinkLocal
class server:
    def __init__(self, number, connection_time = 10):
        os.system("clear")
        self.number = int(number)
        self.connection_time = connection_time
        self.sendinfo = True
        self.dowork = True
        self.waitclients = True
        self.server_work_percentage = 20
        self.unicast_connections = []
        self.intervals_asa_clients = {}
        self.work_done = OrderedDict()
        self.tery = 3
        self.tcp_socket = None
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

    def current_pos(self,number = 0):
        if not number:
            self.tery += 1
        return str(self.tery if not number else number)

    def divide_work(self, initial, final, number_of_clients):
        steps = final/number_of_clients
        print("\033["+self.current_pos()+";0H")
        print("Calculated intervals for distributed work")
        for i in range(1, number_of_clients + 1):
            final_n = final - steps
            steps = ceil(steps + ((final_n) * i/number_of_clients))
            try:
                self.intervals_asa_clients[self.unicast_connections[i - 1]] = (initial, steps)
                self.work_done[(initial, steps)] = None
            except Exception as e:
                print("There are no clients :(")
            print("\033["+self.current_pos()+";0H")
            print("Interval for client " + str(i) + ": ", (initial, steps))
            initial = steps

        for i in range(1, number_of_clients + 1):
            initial = self.intervals_asa_clients[self.unicast_connections[i - 1]][0]
            steps = self.intervals_asa_clients[self.unicast_connections[i - 1]][1]
            if i == 1:
                calculate_int = threading.Thread(name='cal_local_int', target=self.calculate_interval, args=[(initial,steps)])
                calculate_int.start()
                calculate_int.join(1)
            else:
                try:
                    info_to_send = json.dumps({"type": "process", "initial": initial, "final": steps})
                    self.sendToClient(self.unicast_connections[i - 1], info_to_send)
                except Exception as e:
                    print("Error sending to client")

    def calculate_interval(self, interval):
        s = serie()
        r = s.calc(interval)
        print("\033["+self.current_pos()+";0H")
        print("Server calculated response: ")
        print("\033["+self.current_pos()+";0H")
        # print("Calculated "+str(r[0][0]))
        # print("\033["+self.current_pos()+";0H")
        print("Complete interval "+str(r[0][1]))
        print("\033["+self.current_pos()+";0H")
        print("Time "+str(r[1]))
        self.add_work(interval, r[0][1], r[1])

    def add_work(self, interval, calculated_interval, time):
        self.work_done[interval] = (calculated_interval, time)
        if self.checkIfComplete():
            self.calculateErrors()

    def calculateErrors(self):
        total_time = 0
        good_interval = ""
        right_interval = []
        for interval, work in self.work_done.items():
            # print(interval)
            complete_interval = work[0]
            time = work[1]
            # add = self.findCalculatedAtInterval(calculated, complete_interval, good_interval)
            # if add != []:
            #     complete_interval = self.addErrorsTointerval(add, complete_interval)
            # good_interval += self.addToInterval(complete_interval)
            right_interval.extend(complete_interval)
            total_time += float(time)
        print("\033["+self.current_pos()+";0H")
        print("Done with distributed work:")
        print("\033["+self.current_pos()+";0H")
        print("Total time: " + str(total_time))
        print("\033["+self.current_pos()+";0H")
        print("0 to " + str(self.number) + " Interval: ")
        print("\033["+self.current_pos()+";0H")
        print(right_interval)
        self.writeToFile(right_interval, str(total_time))

    def writeToFile(self, interval, time):
        write = ""
        with open("interval.dst", "w") as f:
            for n in interval:
                write += str(n) + " "
            f.write(write)
            f.close()
        with open("time.dst", "w") as f:
            f.write("Time: " + time)
            f.close()

    def addErrorsTointerval(self, add, interval):
        for new in add:
            interval.append(new)
        return sorted(interval)

    def findCalculatedAtInterval(self, calculated, complete_interval, good_interval):
        add = []
        if good_interval != "":
            good_interval += self.addToInterval(complete_interval)
            for n in calculated:
                if str(n) not in good_interval:
                    add.append(n)
        return add

    def addToInterval(self, complete_interval):
        g_i = ""
        for n in complete_interval:
            g_i += str(n)
        return g_i

    def checkIfComplete(self):
        done = False
        for i, w in self.work_done.items():
            if not w:
                break
        else:
            done = True
        return done

    def send_information(self):
        while self.sendinfo:
            time.sleep(0.5)
            self.sendToGroup("Hi")
        print("\033["+self.current_pos(3)+";0H")
        print("Multicast: Sent finished                       ")
        self.divide_work(0, self.number, len(self.unicast_connections))

    def waitTCPCLients(self, interface):
        print("\033["+self.current_pos()+";0H")
        try:
            addr = socket.getaddrinfo(getOwnLinkLocal(interface) + '%' + interface, self.MYPORT - 10, socket.AF_INET6, 0, socket.SOL_TCP)[0]
            self.tcp_socket = socket.socket(addr[0], socket.SOCK_STREAM)
            self.tcp_socket.bind(addr[-1])
            self.tcp_socket.listen(10)
            self.unicast_connections.append(self.tcp_socket)
        except Exception as e:
            print("Error connecting")
            self.tcp_socket.close()
        print("\033["+self.current_pos()+";0H")
        print ("Waiting for TCP connections, address: '%s'" % str(addr[-1][0]))
        while self.waitclients:
            try:
                conn, address = self.tcp_socket.accept()
                print("\033["+self.current_pos()+";0H")
                print("Connection stablished with client " + "#" + str(len(self.unicast_connections)) + " " + str(address))
                self.unicast_connections.append(conn)
                new_con = threading.Thread(name='tcpConnection', target=self.tcpConnection, args=[conn])
                new_con.start()
                new_con.join(1)
            except Exception as e:
                print(e)
                self.waitclients = False
        print("Closing connections")
        # self.tcp_socket.close()
        # for sock in self.unicast_connections:
        #     sock.close()

    def tcpConnection(self, client):
        data = ""
        try:
            self.sendToClient(client, "hi")
            while self.dowork:
                data = client.recv(1024*100)
                if len(data):
                    print("\033["+self.current_pos()+";0H")
                    print('Received from one client:', data)
                    self.checkData(data)
        except Exception as e:
            print(e)
        print("Closing connection with gone client")
        if self.intervals_asa_clients[client]:
            print("Going to calculate its data")
            initial = self.intervals_asa_clients[client][0]
            steps = self.intervals_asa_clients[client][1]
            calculate_int = threading.Thread(name='cal_local_int', target=self.calculate_interval, args=[(initial,steps)])
            calculate_int.start()
            calculate_int.join(1)
        client.close()
    def checkData(self, data):
        try:
            data = json.loads(data.decode())
            if data["type"] == "response":
                print("\033["+self.current_pos()+";0H")
                print("Client responded: ")
                print("\033["+self.current_pos()+";0H")
                print("Complete interval "+str(data["interval"]))
                print("\033["+self.current_pos()+";0H")
                print("Time "+str(data["time"]))
                self.add_work((int(data["initial"]), int(data["final"])),  data["interval"], data["time"])
        except Exception as e:
            print(e)
            print("No json")

    def wait_connection(self):
        for i in range(1, int(self.connection_time) + 1):
            time.sleep(1)
            print("\033["+self.current_pos(2)+";0H")
            print("Ana's serie: Beginning in " + str(i))
        print("\033["+self.current_pos(2)+";0H")
        print("Ana's serie: Information will be sent to clients now!")
        self.sendinfo = False

    def sendToClient(self, client, data):
        print("\033["+self.current_pos()+";0H")
        print ('Sending to client :', data)
        client.send(data.encode())

    def sendToGroup(self, message):
        print("\033["+self.current_pos(3)+";0H"+"\nMulticast: Sending: " + message)
        self.multicast_sock.sendto(message.encode(), (self.addrinfo[4][0], self.MYPORT))

if __name__ == "__main__":
    try:
	    s = server(sys.argv[1], (sys.argv[2] if len(sys.argv) >= 3 else 10))
    except Exception as e:
        print(e)
        print("Usage: server.py number time-to-begin")
