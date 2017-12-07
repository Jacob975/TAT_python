#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. std_code.py [list name]
editor Jacob975
20171123
#################################
update log

'''
from sys import argv
import numpy as np
import pyfits
import time

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    imA_name=argv[-1]
    imB_name=argv[-2]
    imA = pyfits.getdata(imA_name, dtype = float)
    imB = pyfits.getdata(imB_name, dtype = float)
    imAh = pyfits.getheader(imA_name)
    tuple_list = np.isnan(imA)
    pyfits.writeto("Subtracted.fits", imC, imAh)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
