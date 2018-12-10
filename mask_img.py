#!/usr/bin/python
'''
Program:
    This is a program to mask some data in images. 
Usage: 
    mask_image.py [image file] 
Editor:
    Jacob975
20181210
#################################
update log
20181210 version alpha 1:
    1. The code works.
'''
from astropy.io import fits as pyfits
import numpy as np
import time
from sys import argv
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    if len(argv) != 2:
        print 'The number of arguments is wrong.'
        print 'Usage: mask_image.py [image file]'
        exit() 
    image_name = argv[1]
    #---------------------------------------
    # Load data
    data = pyfits.getdata(image_name)
    header = pyfits.getheader(image_name)
    # Mask
    data[:200] = np.nan
    # Save data
    pyfits.writeto('{0}_mask.fits'.format(image_name[:-4]), data, header)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
