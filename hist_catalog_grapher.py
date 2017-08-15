#!/usr/bin/python
'''
Program:
This is a program to graph histogram of certain property(magnitude usually) vesus numbers.

Usage:
1.  hist_catalog_grapher.py index filename
    
    please don't choose date, band, scope, method, and all stdev of property as your index
    because these property have no stdev behind, which will cause some bugs.

index:
    which column you want to grab
    index could be x_axis, or N_mag

filename:
    which file you read.
    It should generate by get_all_star.py or build_catalog.py

editor Jacob975
20170815
#################################
update log

20170815 version alpha 1
    The code work properly.
'''
from sys import argv
from tat_datactrl import raw_star_catalog_editor
import time

class argv_controller:
    argument = []
    f = ""
    tag_name = ""
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        self.f = argument[-1]
        self.tag_name = argument[-2]
    def filename(self):
        return self.f
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
    catalog = raw_star_catalog_editor(argument.filename())
    # plot the result
    catalog.hist_plot(argument.tag())
    # pause
    raw_input()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
