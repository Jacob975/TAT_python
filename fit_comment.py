#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. fit_comment.py [fits name]
editor Jacob975
20170902
#################################
update log

20170902 version alpha 1
'''
from sys import argv
import time
from astropy.io import fits

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    fits_name=argv[-1]
    end = False
    hdulist = fits.open(fits_name, mode = 'update')
    prihdr = hdulist[0].header
    title = ""
    value = ""
    while not end:
        print "title: "
        title = raw_input()
        if title == 'exit' or value == 'exit':
            end = True
            continue
        print "value: "
        value = raw_input()
        if title == 'exit' or value == 'exit':
            end = True
            continue
        print "If you wanna end, please type in 'exit'"
        prihdr[title] = value
    hdulist.flush()
    hdulist.close()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
