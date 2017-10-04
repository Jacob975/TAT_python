#!/usr/bin/python
'''
Program:
This is a program to convert .tsv file, which is defined by my self, into fits table. 
Usage:
1. tsv2fit.py [start point][file name]

file name:
    The name of the file you want to convert into fits table.

start point:
    where is the start of row of the data(the comment not included).
    If your data is star in the second row, please type 2

example:
    tsv2fit.py 2 some.tsv       # start point will set by 2, some.fits will be generated.
    tsv2fit.py another.tsv      # start point will set by 1 by default, another.fits will be generated.

editor Jacob975
20170830
#################################
update log

20170830 version alpha 1
    The code run properly

20171004 version alpha 2
    Fix a bug of constructing table by columns instead of rows
'''
from sys import argv
import numpy as np
import time
from astropy.table import Table
import tat_datactrl

class argv_controller:
    argument = []
    f = ""
    sp = 1
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        self.f = argument[-1]
        if len(argument) < 2:
            print "No argument"
            print "Usage: tsv2fit.py [start point] [file name]"
            return
        if len(argument) == 3:
            self.sp = argument[-2]
            return
        if len(argument) > 3:
            print "Too many argument"
            print "Usage: tsv2fit.py [start point] [file name]"
            return
    def filename(self):
        return self.f
    def startpoint(self):
        return self.sp

def arr2table(arr, start_point):
    # start_point mean where is the start of data
    if VERBOSE>2: print arr[0]
    print arr[start_point:]
    ans = Table(rows = arr[start_point:], names = np.array(arr[0]))
    if start_point == 2:
        for i in xrange(len(arr[0])):
            ans[arr[0][i]].unit = arr[1][i]
    return ans

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv 
    argument = argv_controller(argv)
    # grab data from tsv
    arr = np.array(tat_datactrl.read_tsv_file(argument.filename()))
    if VERBOSE>2:
        for element in arr:
            print len(element), element
    # convert into table
    t = arr2table(arr, argument.startpoint())
    # save result
    # attention!! This step will overwrite the file with the same name.
    t.write("{0}.fits".format(argument.filename()[:-4]), overwrite = True )
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
