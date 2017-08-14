#!/usr/bin/python
'''
Program:
This is a program to graph the difference of certain property between two data.

Usage:
1.  cmp_grapher.py index filename1 fileanme2
    
    please don't choose date, band, scope, method, and all stdev of property as your index
    because these property have no stdev behind, which will cause some bugs.

index:
    which column you want to grab
    index could be x_axis, or N_mag

filename:
    which file you read.
    It should generate by get_all_star.py or build_catalog.py

editor Jacob975
20170814
#################################
update log

20170814 version alpha 1
    The code work properly.
'''
from sys import argv
from tat_datactrl import raw_star_catalog_comparator
import numpy as np
import pyfits
import time

class argv_controller:
    argument = []
    ref_name = ""
    local_name = ""
    tag_name = ""
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        self.ref_name = argument[-2]
        self.local_name = argument[-1]
        self.tag_name = argument[-3]
    def ref(self):
        return self.ref_name
    def local(self):
        return self.local_name
    def tag(self):
        return self.tag_name

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    argument = argv_controller(argv)
    # read star catalog
    catalog = raw_star_catalog_comparator(argument.ref())
    # plot the result
    catalog.plot(argument.local(), argument.tag())
    # pause
    raw_input()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
