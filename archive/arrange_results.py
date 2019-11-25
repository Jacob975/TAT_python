#!/usr/bin/python
'''
Program:
    This is a program for arranging results from current folder to folder in path of result. 
Usage: 
    arrange_results.py
Editor:
    Jacob975
20180727
#################################
update log
20180727 version alpha 1
    1. the code works
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import time
import TAT_env

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # define the destinate folder for results in path of reduction.
    os.system("rename _subDARK_divFLAT_m.fits _reduce.fits *.fits")
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
