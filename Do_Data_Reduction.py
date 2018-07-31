#!/usr/bin/python
'''
Program:
    This is a program for data reduction on tat. 
Usage: 
    Do_Data_Reduction.py
Editor:
    Jacob975
20170625
#################################
update log
20180625 version alpha 1:
    1. the code works
20180727 version alpha 2:
    1. Update processed list in each loop.
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
    path_of_data = "{0}/{1}/image".format(TAT_env.path_of_image, site)
    path_of_calibrate = "{0}/{1}/calibrate".format(TAT_env.path_of_image, site)
    path_of_log = "{0}/{1}/log".format(TAT_env.path_of_image, site)
    # Load unprocessed data list
    processed_calibrate_list, unprocessed_calibrate_list = unprocessed_check(path_of_log, path_of_calibrate, type_ = "calibrate")
    processed_data_list, unprocessed_data_list = unprocessed_check(path_of_log, path_of_data, type_ = "data")
    
    # Do reduction on calibration 
    failure = undo(unprocessed_calibrate_list)
    failure = check_cal(unprocessed_calibrate_list, processed_calibrate_list, path_of_log)
    # Do reduction on data
    failure = undo(unprocessed_data_list)
    failure = check_arr_sub_div_image(unprocessed_data_list, processed_data_list, path_of_log)
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
def undo(unprocessed_list):
    for unpro in unprocessed_list:
        print unpro
        os.chdir(unpro)
        os.system("{0}/undo_tat_reduction.py".format(TAT_env.path_of_code))
    os.system("cd")
    return 0

# The def for check header and quality of images in calibration.
def check_cal(unprocessed_calibrate_list, processed_calibrate_list, path_of_log):
    # check if input list is empty
    if len(unprocessed_calibrate_list) == 0:
        print "No unprocessed calibrate, check_cal stop"
        return 1
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
            os.system("{0}/check_image.py dark 0 {1}".format(TAT_env.path_of_code, exptime))
        # Flat process
        for band in band_list:
            for exptime in exptime_list:
                os.system("{0}/check_image.py flat {1} {2}".format(TAT_env.path_of_code, band, exptime))
        # if redcution is OK, list the folder in success list.
        if True:
            processed_calibrate_list.append(unpro_cal)
        np.savetxt("{0}/calibrate_reduction_log.txt".format(path_of_log), processed_calibrate_list, fmt="%s")
    return 0

# The def for checking header and quality of data,
# Then arranging these data
# Subtracted by dark
# divided by flat
# save the list of processed data in the end of each loop.
def check_arr_sub_div_image(unprocessed_data_list, processed_data_list, path_of_log):
    # check if input list is empty
    if len(unprocessed_data_list) == 0:
        print "No unprocessed data, check_arr_sub_div_image stop"
        return 1
    band_list = TAT_env.band_list
    success_unpro_data_list = []
    darks_not_found = []
    flats_not_found = []
    psf_register_fail = []
    for unpro_data in unprocessed_data_list:
        #failure_unpro_data = 0
        failure_unpro_data = 1
        print "DIR: {0}".format(unpro_data)
        os.chdir(unpro_data)
        # Check
        for band in band_list:
            os.system("{0}/check_image.py data {1} 0".format(TAT_env.path_of_code, band))
        # Arrange
        os.system("{0}/arrange_images.py".format(TAT_env.path_of_code))
        # find dark and flat
        target_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
        for target in target_list:
            os.chdir(target)
            band_exptime_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
            for band_exptime in band_exptime_list:
                failure = 0
                name_dark = ""
                name_flat = ""
                os.chdir(band_exptime)
                #--------------------------------------------------------------------------
                # check if dark were found.
                try:
                    name_dark = glob.glob("Median_dark_*.fits")[0]
                except:
                    # check if the program success
                    try:
                        # find proper dark
                        os.system("{0}/find_dark.py".format(TAT_env.path_of_code))
                        name_dark = glob.glob("Median_dark_*.fits")[0]
                    except:
                        failure = 1
                        darks_not_found.append("{0}/{1}/{2}".format(unpro_data, target, band_exptime))
                np.savetxt("{0}/darks_not_found.txt".format(path_of_log), darks_not_found, fmt="%s")
                #--------------------------------------------------------------------------
                # check if flat were found
                try:
                    name_flat = glob.glob("Median_flat_*.fits")[0]
                except:
                    # check if the program success
                    try:
                        # find proper flats
                        os.system("{0}/find_flat.py".format(TAT_env.path_of_code))
                        name_flat = glob.glob("Median_flat_*.fits")[0]
                    except:
                        failure = 1
                        flats_not_found.append("{0}/{1}/{2}".format(unpro_data, target, band_exptime))
                np.savetxt("{0}/flats_not_found.txt".format(path_of_log), flats_not_found, fmt="%s")
                #--------------------------------------------------------------------------
                # Subtracted by dark and divided by flat
                try:
                    reducted_images = np.loadtxt("reducted_image_list.txt", dtype = str)    
                except:
                    try:
                        # subtracted by darks and divided by flat
                        os.system("{0}/sub_div.py".format(TAT_env.path_of_code))
                        reducted_images = np.loadtxt("reducted_image_list.txt", dtype = str)    
                    except:
                        failure = 1
                #--------------------------------------------------------------------------
                # psf register
                # try to load registed_image_list, which is produced by register.py
                try: 
                    registed_images = np.loadtxt("registed_image_list.txt", dtype = str)
                    temp_name_space = registed_images[1]
                except:
                    try:
                        os.system("{0}/register.py reducted_image_list.txt".format(TAT_env.path_of_code))
                        registed_images = np.loadtxt("registed_image_list.txt", dtype = str)
                        temp_name_space = registed_images[1]
                    except:
                        failure = 1
                        psf_register_fail.append("{0}/{1}/{2}".format(unpro_data, target, band_exptime))
                # save log infomations
                np.savetxt("{0}/psf_register_fail.txt".format(path_of_log), psf_register_fail, fmt="%s")
                #--------------------------------------------------------------------------
                # Get WCS 
                os.system("{0}/wcsfinder.py registed_image_list.txt".format(TAT_env.path_of_code))
                #--------------------------------------------------------------------------
                # Find targets on images
                os.system("{0}/starfinder.py registed_image_list.txt".format(TAT_env.path_of_code))
                #--------------------------------------------------------------------------
                # Update time series tables 
                os.system("{0}/update_time_series_tables.py table_list".format(TAT_env.path_of_code))
                #--------------------------------------------------------------------------
                # Save results into path of result.
                os.system("{0}/arrange_results.py".format(TAT_env.path_of_code))
                #--------------------------------------------------------------------------
                if failure:
                    failure_unpro_data = 1
                os.chdir('..')
            os.chdir('..')
            # if redcution is OK, list the folder in success list.
        if not failure_unpro_data:
            processed_data_list.append(unpro_data)
        np.savetxt("{0}/data_reduction_log.txt".format(path_of_log), processed_data_list, fmt="%s")
    return 0 

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
