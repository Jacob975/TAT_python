#!/usr/bin/python
'''
Program:
This is a program to read a fits table and print it. 
Usage:
1. fits_table_reader.py [file name]
editor Jacob975

#################################
update log

20170821 version alpha 1
    The code work properly.
'''
from sys import argv
from astropy.table import Table
import numpy as np
import time

class argv_controller:
    argument = []
    filename = ""
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        for i in xrange(len(argument)):
            if i == 0 :
                continue
            if i == 1:
                self.filename = argument[i]
                break
    def name(self):
        return self.filename

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    argument = argv_controller(argv)
    # read table and print out
    t = Table.read(argument.name())
    print t
    print ""
    print t.info
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
