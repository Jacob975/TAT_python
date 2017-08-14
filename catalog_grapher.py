#!/usr/bin/python
'''
Program:
This is a program to graph certain data in tat star catalog.

Usage:
1.  catalog_grapher.py index_1 index_2, ... ,index_n  filename
    
    please don't choose date, band, scope, method, and all stdev of property as your index
    because these property have no stdev behind, which will cause some bugs.

index:
    which column you want to grab
    index_1 will be on x_axis
    else will be on y_axis

filename:
    which file you read.
    It should generate by get_all_star.py or build_catalog.py

editor Jacob975
20170810
#################################
update log

20170810 version alpha 1
    It run properly.

20170814 version alpha 2
    1.  a bug that some data will lost while sorting
    2. move class tsv_editor, star_catalog_editor to tat_datactrl.py
'''
from sys import argv
from tat_datactrl import star_catalog_editor
import numpy as np
import pyfits
import time

class argv_controller:
    argument = []
    filename = ""
    tags = []
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        for i in xrange(len(argument)):
            if i == len(argument) -1:
                self.filename = argument[i]
            elif i == 0:
                continue
            else:
                self.tags.append(argument[i])
                continue
    def name(self):
        return self.filename
    def tag(self):
        return self.tags

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    argument = argv_controller(argv)
    # read star catalog
    catalog = star_catalog_editor(argument.name())
    # plot the result
    catalog.plot(argument.tag())
    # pause
    raw_input()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
