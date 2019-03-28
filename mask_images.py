#!/usr/bin/python
'''
Program:
    This is a program to mask some data in images. 
Usage: 
    mask_images.py [a list of image name] 
Editor:
    Jacob975
20190103
#################################
update log
20190103 version alpha 1:
    1. The code works.
'''
from astropy.io import fits as pyfits
import numpy as np
import time
from sys import argv
import os
import mysqlio_lib
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 2:
        print 'The number of arguments is wrong.'
        print 'Usage: mask_image.py [a list of image name]'
        exit() 
    list_name = argv[1]
    image_name_list = np.loadtxt(list_name, dtype = str)
    #---------------------------------------
    for image_name in image_name_list:
        # Load data
        data = pyfits.getdata(image_name)
        header = pyfits.getheader(image_name)
        # Mask
        data[:200] = np.nan
        # Save data
        new_name = '{0}_mask.fits'.format(image_name[:-5])
        pyfits.writeto( new_name, 
                        data, 
                        header, 
                        overwrite = True)
        print "{0}, done".format(new_name)
        #---------------------------------------
        # Write to database
        cwd = os.getcwd()
        mysqlio_lib.save2sql_images(new_name, cwd)
    # Save the result as a list
    temp = "ls *_mask.fits > masked_image_list.txt"
    os.system(temp)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
