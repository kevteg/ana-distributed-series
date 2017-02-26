#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
class serie:
    def __init__(self, numbers):
        if type(numbers) is not tuple:
            print("Error: numbers are not in a tuple")
        else:
            try:
                self.calc(numbers)
            except Exception as e:
                print("Error: Have you passed all the arguments?")
    def calc(self, numbers):
        numbers_string = ""
        secuence_list = ""
        #Creating long string
        # for n in range(1, numbers[1] + 1):
        #     numbers_string += str(n)

        for n in range(1, numbers[1] + 1):
            if n >= numbers[0] and str(n) in secuence_list:
                print("Found a coincidence " + str(n))
            else:
                secuence_list += str(n)
                numbers_string += str(n) + " "

        print(numbers_string)



if __name__ == "__main__":
    try:
        s = serie((int(sys.argv[1]), int(sys.argv[2])))
    except Exception as e:
        print("Error: It has to be a number")
