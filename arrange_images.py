#!/usr/bin/python
'''
Program:
    The code is used to arrange images into proper folders
Usage: 
    arrange_images.py
Editor:
    Jacob975
20180621
#################################
update log
20180621 version alpha 1
    1. The code works
'''
import os
from astropy.io import fits as pyfits 
import numpy as np
import glob
import time
import TAT_env

def check_sources_info(name_image):
    # load header of images
    try:
        darkh=pyfits.getheader(name_image)
        RA=darkh['RA'].split(':')
        DEC=darkh['DEC'].split(':')
    except:
        print "Warning!\nHeader of {0} is broken".format(name_image)
        command = "mv {0} X_{0}_X".format(name_image)
        os.system(command)
        return 1, ""
    # load header of library, and check if the sources be found in this image.
    for source in sources_list:
        source_RA = source['RA'].split(":")
        source_DEC = source['DEC'].split(":")
        if (float(RA[0]) == float(source_RA[0])) & (float(DEC[0]) == float(source_DEC[0])):
            return 0, source['name']
    print "In {0}, source not found".format(name_image)
    return 1, ""

def check_bands_info(name_image):
    darkh = pyfits.getheader(name_image)
    try:
        band = darkh['FILTER']
        exptime = darkh['EXPTIME']
    except:
        print "Warning!\nHeader of {0} is broken".format(name_image)
        command = "mv {0} X_{0}_X".format(name_image)
        os.system(command)
        return 1, "", 0
    return 0, band, int(exptime)

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #---------------------------------------
    # Initialize
    global sources_list
    sources_list = TAT_env.object_list
    name_image_list = glob.glob('*.fit')
    #---------------------------------------
    # Arrange image to folders
    print "### arrange_image.py ###"
    print "Arrange images into proper directory"
    for name_image in name_image_list:
        # arrange image according to filters and sources type
        failure, source = check_sources_info(name_image)
        if failure:
            continue
        failure, band, exptime = check_bands_info(name_image)
        if failure:
            continue
        new_dir = "{0}/{1}_{2}".format(source, band, exptime)
        # move image to seleted dir, if dir not exist, create a new one.
        command = "mkdir -p {0}".format(new_dir) 
        os.system(command)
        command = "mv {0} {1}".format(name_image, new_dir)
        os.system(command)
        print "{0} ---> {1}".format(name_image, new_dir)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
