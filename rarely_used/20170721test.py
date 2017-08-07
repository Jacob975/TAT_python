#!/usr/bin/python
'''
Program:
This is a program to find the position of each peak, and display the result in ds9.
Usage:
1. test.py [fits]

fits: 
    You should put fits name here, then the code will do it.

2. test.py [list]

list:
    You can also put a list of fits name here, then the code will do all of them seqensly.

    e.g.    $test.py someimg.fits   # find peaks of someimg.fits
            $test.py img_list       # find peaks of imgs mentioned in img_list

editor Jacob975
20170721
#################################
update log
    20170721 version alpha 1
    It could run properly
'''
from sys import argv
import numpy as np
import pyfits
import time
import testlib
import os

#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()
list_name = argv[-1]
list_name_list = list_name.split(".")
if list_name_list[-1] == "fits" or list_name_list[-1] == "fit":
    fits_list = [list_name]
else:
    fits_list=readfile(list_name)

for name in fits_list:
    data = pyfits.getdata(name)
    peak_list = testlib.get_peak_filter(data, size = 30)
    region_name_peak = name[:-5]+".region_peak"
    result_file = open(region_name_peak, "a")
    for i in xrange(len(peak_list)):
        result_file.write("{0} {1}\n".format(peak_list[i][1], peak_list[i][0]))
    result_file.close()
    command = "ds9 -zscale {0} -regions format xy -regions load {1} -zoom to fit &".format(name, region_name_peak)
    os.system(command)
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
