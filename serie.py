#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time
class serie:
    def __init__(self):
	pass
       
    def calc(self, numbers):
        numbers_string = []
        coincidence_string = []
        secuence_list = ""
	if type(numbers) is not tuple:
            print("Error: numbers are not in a tuple")
        else:
            try:
		start = time.time()
                for n in range(1, numbers[1] + 1):
		    if n >= numbers[0] and str(n) in secuence_list:
		        print("Found a coincidence " + str(n))
			coincidence_string.append(n)
		    else:
		        secuence_list += str(n)
			if n >= numbers[0]:
			    numbers_string.append(n)
		end = time.time()
            except Exception as ex:
                print("Error: Have you passed all the arguments?")
        print(end - start)
	return (coincidence_string, numbers_string)

if __name__ == "__main__":
    try:
	s = serie()
	s.calc( (int(sys.argv[1]), int(sys.argv[2])) ) 
    except Exception as e:
	print(e)
        print("Error: It has to be a number")
