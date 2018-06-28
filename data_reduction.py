#!/usr/bin/python
'''
Program:
    This is a program for data reduction on tat. 
Usage: 
    data_reduction.py
Editor:
    Jacob975
20170625
#################################
update log
20180625 version alpha 1:
    1. the code works
'''
import numpy as np
from astropy.io import fits as pyfits
import time
import glob
import TAT_env
import os
import subprocess
import warnings
from starfinder import starfinder, iraf_tbl2reg

def data_reduction(site):
    # Load path
    path_of_data = "{0}/{1}/image".format(TAT_env.path_of_source, site)
    path_of_calibrate = "{0}/{1}/calibrate".format(TAT_env.path_of_source, site)
    path_of_log = "{0}/{1}/log".format(TAT_env.path_of_source, site)
    processed_calibrate_list, unprocessed_calibrate_list = unprocessed_check(path_of_log, path_of_calibrate, type_ = "calibrate")
    processed_data_list, unprocessed_data_list = unprocessed_check(path_of_log, path_of_data, type_ = "data")
    
    # Process calibration first
    failure = flatten(unprocessed_calibrate_list)
    success_unpro_cal_list = check_cal(unprocessed_calibrate_list)
    cal_list = np.append(processed_calibrate_list, success_unpro_cal_list)
    np.savetxt("{0}/calibrate_reduction_log.txt".format(path_of_log), cal_list, fmt="%s")

    # Then process data
    failure = flatten(unprocessed_data_list)
    success_unpro_data_list = check_arr_sub_div_image(unprocessed_data_list)
    data_list = np.append(processed_data_list, success_unpro_data_list)
    np.savetxt("{0}/data_reduction_log.txt".format(path_of_log), data_list, fmt="%s")
    return failure

# The def for checking which date is not processed.
def unprocessed_check(path_of_log, path_of_data, type_):
    # Load processed log data list
    try:
        processed = list(np.loadtxt("{0}/{1}_reduction_log.txt".format(path_of_log, type_), comments = "#", dtype = str))
    except:
        processed = []
    unprocessed = []
    # Match list in folder and log data list
    candidates = glob.glob("{0}/20*".format(path_of_data))
    for candidate in candidates:
        try:
            temp = processed.index(candidate)
        except ValueError:
            unprocessed.append(candidate)
    unprocessed = np.array(unprocessed, dtype = str)
    return processed, unprocessed

# The def for flattening files in a folder.
def flatten(unprocessed_list):
    for unpro in unprocessed_list:
        print unpro
        os.chdir(unpro)
        os.system("flatten_tat_data.py")
    os.system("cd")
    return 0

# The def for check header and quality of images in calibration.
def check_cal(unprocessed_calibrate_list):
    # check if input list is empty
    if len(unprocessed_calibrate_list) == 0:
        print "No unprocessed calibrate, check_cal stop"
        return []
    success_unpro_cal_list = []
    band_list = TAT_env.band_list
    accumulated_exptime_list = []
    for unpro_cal in unprocessed_calibrate_list:
        print "DIR: {0}".format(unpro_cal)
        os.chdir(unpro_cal)
        # Determine exptime
        image_list = glob.glob("{0}/*".format(unpro_cal))
        for name_image in image_list:
            sub_name_1 = name_image.split('x')
            sub_name_2 = sub_name_1[1].split('.fit')
            accumulated_exptime_list.append(sub_name_2[0])
        exptime_list = list(set(accumulated_exptime_list))
        print exptime_list
        # Dark process
        for exptime in exptime_list:
            os.system("check_image.py dark 0 {0}".format(exptime))
        # Flat process
        for band in band_list:
            for exptime in exptime_list:
                os.system("check_image.py flat {0} {1}".format(band, exptime))
        # if redcution is OK, list the folder in success list.
        if True:
            success_unpro_cal_list.append(unpro_cal)
    return success_unpro_cal_list

# The def for checking header and quality of data,
# Then arranging these data
# Subtracted by dark
# divided by flat
def check_arr_sub_div_image(unprocessed_data_list):
    # check if input list is empty
    if len(unprocessed_data_list) == 0:
        print "No unprocessed data, check_arr_sub_div_image stop"
        return []
    band_list = TAT_env.band_list
    success_unpro_data_list = []
    for unpro_data in unprocessed_data_list:
        print "DIR: {0}".format(unpro_data)
        os.chdir(unpro_data)
        # Check
        for band in band_list:
            os.system("check_image.py data {0} 0".format(band))
        # Arrange
        os.system("arrange_images.py")
        # find dark and flat
        target_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
        for target in target_list:
            os.chdir(target)
            band_exptime_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
            for band_exptime in band_exptime_list:
                os.chdir(band_exptime)
                # find proper calibrate
                os.system("find_dark.py")
                os.system("find_flat.py")
                # reduction
                os.system("sub_div.py")
                # psf register
                try: 
                    reducted_images = np.loadtxt("reducted_image_list", dtype = str)
                except:
                    print "psf register fail, no reducted images"
                    os.chdir('..')
                    continue
                else:
                    os.system("new_register.py reducted_image_list")
                    os.chdir('..')
            os.chdir('..')
        # if redcution is OK, list the folder in success list.
        if True:
            success_unpro_data_list.append(unpro_data)
    return success_unpro_data_list

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    warnings.filterwarnings("ignore")
    site_list = TAT_env.site_list

    #---------------------------------------
    # Data reduction
    for site in site_list:
        print "### site {0} ###".format(site)
        failure = data_reduction(site)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
