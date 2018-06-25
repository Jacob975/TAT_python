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

def data_reduction(site):
    # Load path
    path_of_data = "{0}/{1}/image".format(TAT_env.path_of_source, site)
    path_of_calibrate = "{0}/{1}/calibrate".format(TAT_env.path_of_source, site)
    path_of_log = "{0}/{1}/log".format(TAT_env.path_of_source, site)
    processed_calibrate_list, unprocessed_calibrate_list = unprocessed_check(path_of_log, path_of_calibrate, type_ = "calibrate")
    processed_data_list, unprocessed_data_list = unprocessed_check(path_of_log, path_of_data, type_ = "data")
    '''
    # Process calibration first
    failure = flatten(unprocessed_calibrate_list)
    failure = check_cal(unprocessed_calibrate_list)
    cal_list = np.append(processed_calibrate_list, unprocessed_calibrate_list)
    np.savetxt("{0}/calibrate_reduction_log.txt".format(path_of_log), cal_list, fmt="%s")
    '''
    # Then process data
    failure = flatten(unprocessed_data_list)
    failure = check_arr_sub_div_image(unprocessed_data_list)
    data_list = np.append(processed_data_list, unprocessed_data_list)
    np.savetxt("{0}/calibrate_reduction_log.txt".format(path_of_log), data_list, fmt="%s")
    return failure

def unprocessed_check(path_of_log, path_of_data, type_):
    # Load processed log data list
    try:
        processed = np.loadtxt("{0}/{1}_reduction_log.txt".format(path_of_log, type_, fmt="%s"), dtype = str)
    except:
        processed = np.array([])
    unprocessed = []
    # Match list in folder and log data list
    candidates = glob.glob("{0}/*".format(path_of_data))
    for candidate in candidates:
        try:
            temp = processed.index(candidate)
        except:
            unprocessed.append(candidate)
    unprocessed = np.array(unprocessed, dtype = str)
    return processed, unprocessed

def flatten(unprocessed_list):
    for unpro in unprocessed_list:
        print unpro
        os.chdir(unpro)
        os.system("flatten_tat_data.py")
    os.system("cd")
    return 0

def check_cal(unprocessed_calibrate_list):
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
    return 0

def check_arr_sub_div_image(unprocessed_data_list):
    band_list = TAT_env.band_list
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
                os.system("find_dark.py")
                os.system("find_flat.py")
                # reduction
                os.system("sub_div.py")
                os.chdir('..')
            os.chdir('..')
    return 0

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
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
