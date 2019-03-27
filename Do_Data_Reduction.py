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
import time
import glob
import TAT_env
import os
import warnings
import mysqlio_lib
import undo_tat_reduction
from joblib import Parallel, delayed

def data_reduction(site):
    #----------------------------------------------
    # Load where we save data and calibration files 
    path_of_data = "{0}/{1}/image".format(TAT_env.path_of_image, site)
    path_of_calibrate = "{0}/{1}/calibrate".format(TAT_env.path_of_image, site)
    #----------------------------------------------
    # Pick the files which are not processed yet
    unproced_cal_list = unproced_check( path_of_calibrate, 
                                        table_name = TAT_env.ctn_tb_name)
    # Do reduction on calibration 
    failure = undo(unproced_cal_list)
    failure = check_cal(unproced_cal_list)
    #----------------------------------------------
    # Pick the files which are not processed yet
    unproced_data_list = unproced_check(path_of_data, 
                                        table_name = TAT_env.ctn_tb_name)
    # Do reduction on data
    failure = undo(unproced_data_list)
    failure = image_reduction(  unproced_data_list)
    return failure

# The def for checking which date is not processed.
def unproced_check(path_of_data, table_name):
    print ("Check unprocessed calibrations.")
    # Initialized
    unprocessed = []
    processed = []
    #-------------------------------------
    # Load processed log data list
    # Create the database for saving informations.
    mysqlio_lib.create_TAT_tables()
    cnx = mysqlio_lib.TAT_auth()
    cursor = cnx.cursor()
    # Load data from table
    cursor.execute('select `NAME` from TAT.{0}'.format(table_name))
    processed = np.array(cursor.fetchall(), dtype = str).flatten()
    cursor.close()
    cnx.close()
    #-------------------------------------
    # Match list in folder and log data list
    candidates = glob.glob("{0}/20*".format(path_of_data))
    for cand in candidates:
        temp = np.where(processed == cand)
        # Not found
        if len(temp[0]) == 0:
            unprocessed.append(cand)
    unprocessed = np.array(unprocessed, dtype = str)
    return unprocessed

# The def for flattening files in a folder.
def undo(unprocessed_list):
    # Initialized the files saved below.
    for unpro in unprocessed_list:
        print ('--------------------------')
        print unpro
        os.chdir(unpro)
        undo_tat_reduction.undo_tat_reduction()
    os.system("cd")
    return 0

# The def for check header and quality of images in calibration.
def check_cal(unproced_cal_list):
    # check if input list is empty
    if len(unproced_cal_list) == 0:
        print "No unprocessed calibrate, check_cal stop"
        return 0
    #------------------------------
    # Do parallel
    Parallel(   n_jobs=20, 
                prefer="threads")(
                delayed(check_cal_single)(unpro_cal) for unpro_cal in unproced_cal_list)
    return 0

def check_cal_single(unpro_cal):
    band_list = TAT_env.band_list
    accumulated_exptime_list = []
    print "Check DIR: {0}".format(unpro_cal)
    os.chdir(unpro_cal)
    # Determine exptime
    image_list = glob.glob("{0}/*.fit".format(unpro_cal))
    for name_image in image_list:
        sub_name_1 = name_image.split('x')
        sub_name_2 = sub_name_1[1].split('.fit')
        accumulated_exptime_list.append(sub_name_2[0])
    exptime_list = list(set(accumulated_exptime_list))
    # Dark process
    for exptime in exptime_list:
        os.system(  "{0}/check_image.py dark 0 {1} &> /dev/null".format(
                    TAT_env.path_of_code, exptime))
    # Flat process
    for band in band_list:
        for exptime in exptime_list:
            os.system(  "{0}/check_image.py flat {1} {2} &> /dev/null".format(
                        TAT_env.path_of_code, band, exptime))
    #-------------------------------------
    # Save comments and logs into table `container`
    cnx = mysqlio_lib.TAT_auth()
    cursor = cnx.cursor()
    # create data base if not exist
    mysqlio_lib.create_TAT_tables()
    # Save data into the table in the database.
    cursor.execute("INSERT INTO {0} ({1}) VALUES ({2})".format( 
                    TAT_env.ctn_tb_name, 
                    ', '.join(TAT_env.ctn_titles[1:]),
                    ', '.join(['%s'] * len(TAT_env.ctn_titles[1:]))),
                    (unpro_cal, 'Y', 'calibration'))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def im_red_sub():
    #-----------------------------
    # For each container
    print "Check DIR: {0}".format(unpro_data)
    os.chdir(unpro_data)
    # Check
    for band in band_list:
        os.system(  "{0}/check_image.py data {1} 0".format(
                    TAT_env.path_of_code, 
                    band))
    # Arrange
    os.system(  "{0}/arrange_images.py".format(
                TAT_env.path_of_code))
    # find dark and flat
    target_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
    for target in target_list:
        os.chdir(target)
        band_exptime_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
        Parallel(   n_jobs=5)(
                    delayed(im_red_subsub)(band_exptime) for band_exptime in band_exptime_list)
        os.chdir('..')
    return 0

def im_red_subsub(band_exptime):
    os.chdir(band_exptime)
    #--------------------------------------------------------------------------
    # check if dark were found. If no, find one.
    try:
        name_dark = glob.glob("Median_dark_*.fits")[0]
    except:
        os.system("{0}/find_dark.py &> /dev/null".format(TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    # check if flat were found. If no, find one.
    try:
        name_flat = glob.glob("Median_flat_*.fits")[0]
    except:
        os.system("{0}/find_flat.py &> /dev/null".format(TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    # Subtracted by dark and divided by flat
    try:
        reducted_images = np.loadtxt("reducted_image_list.txt", dtype = str)    
    except:
        # subtracted by darks and divided by flat
        os.system("{0}/sub_div.py  &> /dev/null".format(TAT_env.path_of_code))
    ''' check point '''
    os.chdir('..')
    return 0
    #--------------------------------------------------------------------------
    # Mask the bad pixels
    try:
        masked_images = np.loadtxt("masked_image_list.txt", dtype = str)    
    except:
        # Mask the bad pixels 
        os.system(  "{0}/mask_images.py reducted_image_list.txt  &> /dev/null".format(
                    TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    # PSF register
    # try to load registed_image_list, which is produced by register.py
    try: 
        registed_images = np.loadtxt("registed_image_list.txt", dtype = str)
    except:
        os.system(  "{0}/register.py masked_image_list.txt".format(
                    TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    # Upload the information of all image to mysql database.
    os.system("{0}/update_to_TAT_db.py".format(TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    # Get WCS 
    os.system(  "{0}/wcsfinder.py registed_image_list.txt".format(
                TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    # Find targets on images
    # Update to database.
    os.system(  "{0}/starfinder.py registed_image_list.txt".format(
                TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    # Do more CATA photometry.
    os.system("{0}/photometry.py CATA {0} {1}".format(start_date, end_date))
    #--------------------------------------------------------------------------
    # Save results into path of result.
    os.system("{0}/arrange_results.py".format(TAT_env.path_of_code))
    #--------------------------------------------------------------------------
    os.chdir('..')

def im_red_sub():
    #-----------------------------
    # For each container
    print "Check DIR: {0}".format(unpro_data)
    os.chdir(unpro_data)
    # Check
    for band in TAT_env.band_list:
        os.system(  "{0}/check_image.py data {1} 0".format(
                    TAT_env.path_of_code, 
                    band))
    # Arrange
    os.system(  "{0}/arrange_images.py".format(
                TAT_env.path_of_code))
    # find dark and flat
    target_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
    for target in target_list:
        os.chdir(target)
        band_exptime_list = [d for d in os.listdir(os.getcwd()) if os.path.isdir(d)] 
        Parallel(   n_jobs=5)(
                    delayed(im_red_subsub)(band_exptime) for band_exptime in band_exptime_list)
        os.chdir('..')
    return 0

def image_reduction(unprocessed_data_list): 
    # check if input list is empty
    if len(unprocessed_data_list) == 0:
        print "No unprocessed data, image_reduction stop"
        return 1
    # Do it parallel
    Parallel(   n_jobs=20)(
                delayed(im_red_sub)(unpro_data) for unpro_data in unprocessed_data_list)
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
