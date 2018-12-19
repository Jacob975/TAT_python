#!/usr/bin/python
'''
Program:
    This is a program for stacking images in list.
Usage: 
    stack.py [image list]
Editor:
    Jacob975
20170216
#################################
update log
20180716 version alpha 1
    1. The code work
'''
import os 
from astropy.io import fits as pyfits
from sys import argv
import numpy as np
import time

def stack_mdn_method(fits_list):
    data_list = []
    for name in fits_list:
        data = pyfits.getdata(name)
        data_list.append(data)
    data_list = np.array(data_list)
    sum_fits = np.median(data_list, axis = 0)
    return sum_fits

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 2:
        print "Wrong numbers of arguments"
        print "Usage: stack.py [image list]"
        exit()
    name_list = argv[1]
    image_name_list = np.loadtxt(name_list, dtype = str)
    #----------------------------------------
    # Stack images
    sum_fits = stack_mdn_method(image_name_list)
    header = pyfits.getheader(image_name_list[len(image_name_list)/2])
    #pyfits.writeto("stacked_image.fits", sum_fits, header, overwrite = True)
    pyfits.writeto("{0}.fits".format(name_list[:-4]), sum_fits, header, overwrite = True)
    #----------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
