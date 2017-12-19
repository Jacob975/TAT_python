#!/usr/bin/python
'''
Program:
This is a program to show a plot of hist gaussian fitting 
Usage:
1. 20171130demo.py [fits name]
editor Jacob975
20171130
#################################
update log

    20171130 version alpha 1
        The demo works well
'''
from sys import argv
from math import pow
import numpy as np
import pyfits
import time
import curvefit

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    fits_name = argv[-1]
    imA = pyfits.getdata(fits_name)
    paras, cov = curvefit.hist_gaussian_fitting("picture", imA, half_width = 100, shift = -10, VERBOSE =4)
    raw_input()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
