#!/usr/bin/python
'''
Program:
This is a code to drop star info from ds9,
info include mag of stars, R.A, DEC., orbital paras, etc...

Usage:
1. get_w_stls.py [band] [fits name]
band:
    It should be a string.
    e.g. 'N'
    This is used to choose which catalog will be used.
    default: 'N'

fits name:
    Literally, you should put a fits name here.
    This fits should have wcs coor.
    So on it is not available from process a list of fits,
    please once type a fits name.

example:
    $get_w_stls.py V fitname.fits
    $get_w_stls.py another.fits

editor Jacob975
20170707
#################################
update log
    20170707 alpha 1
    This code can run properly

    20170718 alpha 2 
    1.  add the command about V band.
    2.  delete the variable about controll catalog filter.

    20170719 alpha 3 
    1.  add the command about U, B, R, I.

    20170829 alpha 4 
    1.  change name of saves in order to match the need of new datatype, fits.
'''

from sys import argv, exit
import os
import numpy as np
import pyfits
import time

def get_img_property(image_name):
    image_name_list = image_name.split("_")
    try:
        scope_name = image_name_list[0]
        date_name = image_name_list[1]
        obj_name = image_name_list[2]
        filter_name = "{0}_{1}".format(image_name_list[3], image_name_list[4])
    except:
        print "Inproper name, get property changing ot dir"
        path = os.getcwd()
        list_path = path.split("/")
        scope_name = list_path[-5]
        date_name = list_path[-3]
        obj_name = list_path[-2]
        filter_name = list_path[-1]
    method = image_name_list[-2]
    return scope_name, date_name, obj_name, filter_name, method

#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()
# get info from argv, include filename(required) and limitation(optional)
fits_name = argv[-1]
band = argv[-2]

scope_name, date_name, obj_name, filter_name, method = get_img_property(fits_name)

# different band will correspond to different database.
command = ""
if band == "N":
    command = "ds9 {0} -catalog gsc1.2 -catalog filter '$Pmag > 0' -catalog export tsv {1}_{2}_{3}.tsv -exit".format(fits_name, scope_name, obj_name, band)
elif band == "U":
    command = "ds9 {0} -catalog sdss8 -catalog filter '$umag > 0' -catalog export tsv {1}_{2}_{3}.tsv -exit".format(fits_name, scope_name, obj_name, band)
elif band == "B":
    command = "ds9 {0} -catalog gsc2.3 -catalog filter '$jmag > 0' -catalog export tsv {1}_{2}_{3}.tsv -exit".format(fits_name, scope_name, obj_name, band)
elif band == "V":
    command = "ds9 {0} -catalog gsc2.3 -catalog filter '$Vmag > 0' -catalog export tsv {1}_{2}_{3}.tsv -exit".format(fits_name, scope_name, obj_name, band)
elif band == "R":
    command = "ds9 {0} -catalog gsc2.3 -catalog filter '$Fmag > 0' -catalog export tsv {1}_{2}_{3}.tsv -exit".format(fits_name, scope_name, obj_name, band)
elif band == "I":
    command = "ds9 {0} -catalog gsc2.3 -catalog filter '$Nmag > 0' -catalog export tsv {1}_{2}_{3}.tsv -exit".format(fits_name, scope_name, obj_name, band)
else:
    print "Unable to identifiy the band,\nUsing default: N."
    command = "ds9 {0} -catalog gsc1.2 -catalog filter '$Pmag > 0' -catalog export tsv {1}_{2}.tsv -exit".format(fits_name, scope_name, obj_name)
if VERBOSE>2:print command
os.system(command)    
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
