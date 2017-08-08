#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. std_code.py [list name]
editor Jacob975
20170318
#################################
update log
    20170318 version alpha 1
        This code is made for convenient constructing new code.
    
    20170626 version alpha 2 
    1. change name method to Usage
    2. add VERBOSE
        In detail 
        VERBOSE == 0 means no print 
        VERBOSE == 1 means printing limited result
        VERBOSE == 2 means graphing a plot or printing more detailed result
        VERBOSE == 3 means printing debug imfo
    
    20170719 version alpha 3
    1.  delete usless part, finding stdev.
    2.  add a func of reading .tsv file.
'''
from sys import argv
from math import pow
import numpy as np
import pyfits
import time

#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()
# get property from argv
list_name=argv[-1]
fits_list=readfile(list_name)

# do what you want.


# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
