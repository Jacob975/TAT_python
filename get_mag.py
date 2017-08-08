#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. get_mag.py [eccentricity] [band] [fits name]

eccentricity
    This is a option to limit the eccentricity of local found star catalog
    from 0 to 1 is proper, over this range will disable this limitation.
    default : 0.9

band
    This is a option, controlling which kind of database will be drop.
    It is a option with default value: "N".

fits name
    You should put a fits name over there.
    and this fit should come with wcs coord.
    method will be set by the hint in fits name

e.g $get_mag.py Median_mdn_w.fits       # method will be set as 'mdn'
    $get_mag.py V Median_mdn_w.fits     # method will be set as 'mdn', band will be set as V band
editor Jacob975
20170710
#################################
update log
    20170710 version alpha 1
        This code can run properly.

    20170711 version alpha 2
        1. This code will save data in /home/Jacob975/demo/20170605_meeting/delta_mag.tsv
            details is writen in header.
        2. Now you can not only put in file to generate result but also put in fits
            details is writen in header.

    20170717 version alpha 3
        1.  When calculating the delta magnitude, It will do error transmission from ref data.
            not just take the standard deviation of stars' magnitude.
        2.  So on the error of instrument magnitude is not been measured by gaussian 2D fitting,
            we just skip it until well done.

    20170718 version alpha 4 
        1.  Rolling back the change of alpha 3
            Base on statistic, when findding the stdev for a lot of data with error.
            We should do statistic by weight, which is controlled by error.
            not just pass the error of themself.

            try to think about a question, A and B are value.
            A = 100 +- 0.1
            B = 0 +- 0.1
            what is their stdev?
            I'm pretty sure that is not 0.141, It should be much greater.

            So on I don't statistic by weight, because the structure of math haven't be constructed.
        2.  now you cannot use this code with only local catalog and ref catalog
            you can only using the fits with wcs and band letter.
        3.  add a new option ecc to limit the eccentricity of local found star catalog.

    20170718 version alpha 5
        1.  add the ability to process band U, B, V, R, I.
    
    20170728 version alpha 6
        1.  Update the func of error magnitude, now it will be generate by weighted average and stdev.
        2.  fix some bugs about nan. or inf. come into calculation.

    20170808 version alpha 7
        1.  use tat_config to control path of result data instead of fix the path in the code.
'''
from sys import argv, exit
import numpy as np
import pyfits
import time
import curvefit
import os
import math
import tat_datactrl

# This is a code to add several stars, and then find out the equivelent magnitude.
def get_add_mag(matched_array, band):
    mag_array = []
    # for different band, the position of mag is different.
    if band == "N":
        mag_array = np.array(matched_array[:,6], dtype = float)
    elif band == "U":
        mag_array = np.array(matched_array[:,11], dtype = float)
    elif band == "B":
        mag_array = np.array(matched_array[:,7], dtype = float)
    elif band == "V":
        mag_array = np.array(matched_array[:,8], dtype = float)
    elif band == "R":
        mag_array = np.array(matched_array[:,6], dtype = float)
    elif band == "I":
        mag_array = np.array(matched_array[:,9], dtype = float)
    count_array = curvefit.mag2count(mag_array)
    count = np.sum(count_array)
    mag = curvefit.count2mag(count)
    return mag

# This is a code to mean several delta_m, and then find out the equivelent magnitude.
def weighted_avg_and_std(values, weights):
    #Return the weighted average and standard deviation.
    #values, weights -- Numpy ndarrays with the same shape.
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)  # Fast and numerically precise
    return average, math.sqrt(variance)

# get property of images from path
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
VERBOSE = 1
# measure times
start_time = time.time()
# get all names of fits
if len(argv) == 1:
    print "No parameters"
    exit(0)
image_name = argv[-1]
band = "N"
ecc = 0.9
if len(argv) > 2:
    band = argv[-2]
if len(argv) > 3:
    ecc = argv[-3]

local_file = "{0}_stls.tsv".format(image_name[:-5])
ref_file = "{0}_{1}.tsv".format(image_name[:-5], band)

# get star catalog from local img and drop star catalog from online database.
temp = "rm *stls.tsv".format(band)
os.system(temp)
os.system("get_info.py {1} {0}".format(image_name, ecc))
os.system("get_w_stls.py {1} {0}".format(image_name, band))
# get property of images from path
scope_name, date_name, obj_name, filter_name, method = get_img_property(image_name)

# read data from files, and create a list to put these data.
ref_catalog = tat_datactrl.read_tsv_file(ref_file)
local_catalog = tat_datactrl.read_tsv_file(local_file)
# match stars by wcs
delta_m_list = []
e_delta_m_list = []
# the merge is about a pixel in wcs
merge = 0.001
for i in xrange(len(local_catalog)):
    matched_list = []
    if i < 2:
        continue
    local_mag = float(local_catalog[i][10])
    for j in xrange(len(ref_catalog)):
        if j == 0:
            continue
        _RA = float(ref_catalog[j][0])
        RA = float(local_catalog[i][0])
        _DEC = float(ref_catalog[j][1])
        DEC = float(local_catalog[i][2])
        # because the resolution of telescope, we tolerate a range for matching stars.
        the_same_RA = bool(RA - merge < _RA and RA + merge > _RA )
        the_same_DEC = bool(DEC - merge < _DEC and DEC + merge > _DEC)
        if the_same_RA and the_same_DEC:
            matched_list.append(ref_catalog[j])
            if VERBOSE>1:
                print "Belows are the same"
                print "local_pos: {0}, {1}".format(RA, DEC)
                print "ref_pos: {0}, {1}".format(_RA, _DEC)
                print "mag = {0}+-{1}".format(local_catalog[i][10], local_catalog[i][11])
                print "Ref_mag = "+ref_catalog[j][6]
    if len(matched_list) == 0:
        print "no matched star"
        continue
    matched_list = np.array(matched_list)
    ref_mag = get_add_mag(matched_list, band)
    delta_mag = ref_mag - local_mag
    e_mag = float(local_catalog[i][11])
    if np.isnan(e_mag) or np.isinf(e_mag):
        continue
    if np.isnan(delta_mag) or np.isinf(delta_mag):
        continue
    delta_m_list.append(delta_mag)
    e_delta_m_list.append(e_mag)
    if VERBOSE>0:
        print "ref_mag: {0:.2f}, local_mag: {1:.2f}+-{3:.2f}, delta: {2:.2f}+-{3:.2f}".format(ref_mag, local_mag, delta_mag, e_mag)
# calculate the delta of magnitude.
delta_m_list = np.array(delta_m_list)
e_delta_m_list = np.array(e_delta_m_list)
delta_m_list, e_delta_m_list = curvefit.get_rid_of_exotic_vector(delta_m_list, e_delta_m_list)
result_delta_m, result_delta_std = weighted_avg_and_std(delta_m_list, e_delta_m_list)
if VERBOSE>0:print "In average, delta_mag = {0:.2f}+-{1:.2f}".format(result_delta_m, result_delta_std)
# save result
path_of_result = tat_datactrl.get_path("result")
result_file = open("{0}/limitation_magnitude_and_noise/delta_mag.tsv".format(path_of_result), 'a')
if float(ecc) > 0 and float(ecc) < 1: 
    writen_ecc = ecc
else:
    writen_ecc = "N"
result_file.write("{0:.2f}\t{1:.2f}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\n".format(result_delta_m, result_delta_std, obj_name, scope_name, filter_name, date_name, method, band, writen_ecc))
result_file.close()
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
