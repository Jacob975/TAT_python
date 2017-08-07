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
    20170318
        This code is made for convenient constructing new code.
    20170626 version alpha 2 
    1. change name method to Usage
    2. add VERBOSE
        In detail 
        VERBOSE == 0 means no print 
        VERBOSE == 1 means printing limited result
        VERBOSE == 2 means graphing a plot or printing more detailed result
        VERBOSE == 3 means printing debug imfo
'''

from sys import argv
import numpy as np
import pyfits
import time
import curvefit

def mag2count(mag, error_mag):
    # prototype: count = 10^(mag / -2.5)
    temp_1 = np.divide(mag, -2.5)
    count = np.power(10, temp_1)
    temp_2 = np.add(mag, error_mag)
    temp_2 = np.divide(temp_2, -2.5)
    error_count = np.power(10, temp_2) - np.power(10, temp_1)
    return count, error_count

def count2mag(count, error_count):
    # prototype: mag = -2.5 * log10( count )
    mag = -2.5*np.log10(count)
    temp = np.add(count, error_count)
    error_mag = -2.5*np.log10(count) + 2.5*np.log10(temp)
    return mag, error_mag

#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()

test_list = [2, 3, 4, 5]
test_error_list = [0.1, 0.1, 0.1, 0.1]

count, error_count = mag2count(test_list, test_error_list)
print count
print error_count
value, error = curvefit.error_transmission(count, error_count, sign = "*")
print "{0}+-{1}".format(value, error)

# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
