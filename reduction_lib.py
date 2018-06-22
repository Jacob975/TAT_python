#!/usr/bin/python
'''
Program:
    This is a library for data reduction 
Usage: 
    import reduction_lib.py
Editor:
    Jacob975
20180621
#################################
update log
20180621 version alpha 1
    1. the code looks good.
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import time

# This is used to generate subDARK fits
def subtract_images(image_list, dark_name):
    dark = pyfits.getdata(dark_name)
    for name in image_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imB = np.subtract(imA, dark)
        sub_name = name[:-4] 
        new_name = "{0}_subDARK.fits".format(sub_name)
        pyfits.writeto(new_name, imB, imAh, overwrite = True)
        print "{0}, OK".format(new_name)
    return

# This is used to generate divFLAT fits
def division_images(image_list, flat_name):
    flat = pyfits.getdata(flat_name)
    for name in fits_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imB = np.divide(imA, flat)
        sub_name = name[:-4] 
        new_name = "{0}_divFLAT.fits".format(sub_name)
        pyfits.writeto(new_name, imB, imAh, overwrite = True)
        print "{0}, OK ".format(new_name)
    return
