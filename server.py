#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import time
import serie
import threading
class server:
    def __init__(self, number, connection_time = 10):
	self.number = number
	self.connection_time = connection_time
	wait_connection = threading.Thread( name='wait_connection', target=self.wait_connection)
        wait_connection.start()
        wait_connection.join(1)
       
    def divide_work(self):
        pass
    def wait_connection(self):
	os.system("clear")
	for i in range(1, int(self.connection_time) + 1):
	     time.sleep(1)
	     print "\033[0;0H"
	     print("Beginning in " + str(i))
	print("BOOM")

if __name__ == "__main__":
    try:
	s = server(sys.argv[1], sys.argv[2] if len(sys.argv) >= 3 else 10)

    except Exception as e:
	print(e)
        print("Error: It has to be a number")
