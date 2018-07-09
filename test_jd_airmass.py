#!/usr/bin/python
'''
Program:
    This is a program for converting Julian date(JD) to Heliocentric Julian date(HJD), Barycentric Julian date(BJD), and air mass. 
    Then add these infos into the header of images.
Usage: 
    test_jd_airmass.py [image name]
Editor:
    Jacob975
20180709
#################################
update log
20180709 version alpha 1
    1. The code works
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import time
from sys import argv
from reduction_lib import header_editor

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print "Error!Wrong numbers of arguments"
        print "Usage: test_jd.py [image name]"
        exit()
    name_image = argv[1]
    #---------------------------------------
    # Load header
    header = pyfits.getheader(argv[1])
    # Test class-style functions
    stu = header_editor(header)
    print "hjd = {0}, bjd = {1}, air mass = {2}".format(stu.hjd(), stu.bjd(), stu.air_mass())
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
