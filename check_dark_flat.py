#!/usr/bin/python
'''
Program:
    This is a easier way to test the completeness of CCDTEMP, EXPTIME
    It also check if CCDTEMP < -29.5 deg.
Usage: 
    check_dark_flat.py
Editor:
    Jacob975
20180622
#################################
update log
20180621 alaph 6
    1. rename the code
    2. Make the code simpler
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import glob
import time
from data_reduction import check_header, bkg_info

#--------------------------------------------
# main code
if __name__ == "__main__":
    # measure times
    start_time = time.time()
    #----------------------------------------
    # Completeness check
    # make a list with names of images in this directory
    image_list = glob.glob('*dark*.fit')
    # check the valid of image_list
    if len(image_list) == 0:
        print "Error!\nNo image found"
        exit()
    #---------------------------------------
    # Initialize
    # There are the parameters of header infos
    PARAS=['CCDTEMP','EXPTIME']
    bad_headers = []
    print "### data reduction ###"
    #---------------------------------------
    # Header and check
    # check headers of images, then load mean and std of background.
    for name_image in image_list:
        failure = check_header(name_image, PARAS)
        if failure:
            bad_headers.append(1)
            command = "mv {0} X_{0}_X".format(name_image)
            os.system(command)
            continue
        bad_headers.append(0)
        print name_image, ",checked"
    #----------------------------------------
    print "### Check finished! ###"
    print "Number of total image: {0}".format(len(image_list))
    print "Number of success: {0}".format(len(image_list) - np.sum(bad_headers, dtype = int)) 
    print "Number of broken header: {0}".format(np.sum(bad_headers, dtype = int))
    #---------------------------------------
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
