#!/usr/bin/python
'''
Program:
    This is a program for finding wcs coordinate.
Usage: 
    wcsfinder.py [a images list]
Editor:
    Jacob975
20180724
#################################
update log
20180723 version alpha 1
    1. The code works.
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import glob
import time
from sys import argv

# Stack images by median
def stack(image_list):
    data_list = []
    for name in image_list:
        data = pyfits.getdata(name)
        data_list.append(data)
    data_list = np.array(data_list)
    stacked_image = np.median(data_list, axis = 0)
    return stacked_image

# Get WCS with astrometry programy
def get_wcs(image_name):
    try:
        # Load if existing already.
        header_wcs = pyfits.getheader("{0}.wcs".format(image_name[:-5]))
    except:
        astrometry_program = "/opt/astrometry/bin/solve-field"
        command = "{0} {1} --overwrite".format(astrometry_program, image_name)
        os.system(command)
        '''
        astrometry_program = "/opt/astrometry/bin/solve-field"
        astrometry_engine = "/opt/astrometry/bin/astrometry-engine"
        # Produce wcs header with astrometry
        command = "{0} {1} --overwrite --just-augment".format(astrometry_program, image_name)
        os.system(command)
        command = "{0} -i /opt/astrometry/data_test/index-4207*.fits {0}.axy".format(astrometry_engine, image_name[:-5])
        os.system(command)
        '''
        # Load the file
        try:
            header_wcs = pyfits.getheader("{0}.wcs".format(image_name[:-5]))
        except:
            print "solve-field fail, no wcs reference."
            return 1, None
    return 0, header_wcs

def clean_astrometry_product():
    command = 'rm -f *.axy *.corr *.png *.xyls *.match *.rdls *.solved'
    os.system(command)

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 2:
        print "Wrong numbers of arguments"
        print "Usage: wcsfinder.py [a images list]"
        exit(1)
    name_of_image_list = argv[1]
    image_list = np.loadtxt(name_of_image_list, dtype = str)
    #---------------------------------------
    # Stack images for better sensitivity
    try:
        stacked_image = stack(image_list)
    except:
        print "No enough images for finding WCS"
        exit(1)
    # Save stacked image
    name_stacked_image = 'stacked_image.fits'
    pyfits.writeto(name_stacked_image, stacked_image ,overwrite = True)
    # Find wcs for the stacked image
    failure, heaer_wcs = get_wcs(name_stacked_image)
    if failure:
        print "WCS coordinate not found"
        exit(1)
    clean_astrometry_product()
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
