#!/usr/bin/python
'''
Program:
    This is a program to
    1. subtract images by darks
    2. flatten images by flats
    3. rotate images to true position. 
Usage: 
    sub_div_r_temp.py
Editor:
    Jacob975
20170622
#################################
update log
20180621 alaph 6
    1. The code looks good
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import glob
import time
import TAT_env
from reduction_lib import subtract_images, divide_images

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #---------------------------------------
    # Initialize
    image_list = glob.glob("*.fit")
    imAh = pyfits.getheader(image_list[0])
    try:
        site = imAh["OBSERVAT"]
    except:
        path=os.getcwd()
        path_of_image = TAT_env.path_of_image
        temp_path = path.split(path_of_image)
        temp_path_2 = temp_path[1].split("/")
        site = temp_path_2[1] 
    # Check if dark and flat exist.
    try:
        name_dark = glob.glob("Median_dark*")[0]
        name_flat = glob.glob("Median_flat*")[0]
    except:  
        print("reduction fail, no enough darks or flats")
        exit(1)
    #---------------------------------------
    # Subtraction and Division
    subdark_image_list = subtract_images(image_list, name_dark)
    divflat_image_list = divide_images(subdark_image_list, name_flat)
    # Save a list of images
    temp = "rm *subDARK.fits"
    os.system(temp)
    temp = "ls *divFLAT.fits > reducted_image_list.txt"
    os.system(temp)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
