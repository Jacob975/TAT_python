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

#---------------------------------------------------------------------
# basic fits processing

# This is used to rotate img
# The direction needed to modified.
def rotate_images(image_list, site):
    if site == "KU":
        for name in image_list:
            imA=pyfits.getdata(name)
            imAh=pyfits.getheader(name)
            imC = np.rot90(imA, 2)
            imC = np.fliplr(imC)
            pyfits.writeto(name[0:-5]+'_r.fits', imC, imAh)
            print name[0:-5]+"_r.fits OK"
    elif site == "TF":
        for name in image_list:
            imA=pyfits.getdata(name)
            imAh=pyfits.getheader(name)
            imC = np.rot90(imA, 2)
            imC = np.fliplr(imC)
            pyfits.writeto(name[0:-5]+'_r.fits', imC, imAh)
            print name[0:-5]+"_r.fits OK"
    return

# This is used to generate subDARK fits
def subtract_images(image_list, dark_name):
    dark = pyfits.getdata(dark_name)
    new_image_list = []
    for name in image_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imB = np.subtract(imA, dark)
        sub_name = name.split(".")[0] 
        new_name = "{0}_subDARK.fits".format(sub_name)
        new_image_list.append(new_name)
        pyfits.writeto(new_name, imB, imAh, overwrite = True)
        print "{0}, OK".format(new_name)
    return new_image_list

# This is used to generate divFLAT fits
def divide_images(image_list, flat_name):
    flat = pyfits.getdata(flat_name)
    new_image_list = []
    for name in image_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imB = np.divide(imA, flat)
        sub_name = name.split(".")[0] 
        new_name = "{0}_divFLAT.fits".format(sub_name)
        new_image_list.append(new_name)
        pyfits.writeto(new_name, imB, imAh, overwrite = True)
        print "{0}, OK ".format(new_name)
    return new_image_list


