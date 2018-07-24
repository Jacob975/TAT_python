#!/usr/bin/python
'''
Program:
    This is a code for fix wrong filter infos in header 
Usage: 
    fix_header.py [image_name_list]
Editor:
    Jacob975
20180716
#################################
update log
20180716 version alpha 1
    1. The code works
'''
import os 
from astropy.io import fits as pyfits
from sys import argv
import numpy as np
import time

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print "Wrong numbers of arguments"
        print "Usage: fix_header.py [imaage_name_list]"
        exit(1)
    try:
        image_name_list = np.loadtxt(argv[1], dtype = str)
    except:
        print "No images in {0}".format(argv[1])
        exit(1)
    #---------------------------------------
    # Update filter infos in header 1 by 1
    for image_name in image_name_list:
        true_filter = image_name[0]
        data = pyfits.getdata(image_name)
        header = pyfits.getheader(image_name)
        try:
            original_filter = header['FILTER']
        except:
            original_filter = 'X'
        print "{0}, {1} --- > {2}".format(image_name, original_filter, true_filter)
        header['FILTER'] = true_filter
        pyfits.writeto(image_name, data, header, overwrite = True)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
