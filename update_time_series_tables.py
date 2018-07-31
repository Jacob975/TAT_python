#!/usr/bin/python
'''
Program:
    This is a program for convert target on frames table to target light curve table 
Usage: 
    update_time_series_tables.py [table list]
Editor:
    Jacob975
20180723
#################################
update log
20180723 version alpha 1
    1. The code works.
'''
import os 
from astropy.io import fits as pyfits
from sys import argv
import numpy as np
import time
import TAT_env
import glob
import re

# The def find the match name of target names.
def match_names(target, tolerance):
    ra = float(target[5])
    dec = float(target[6])
    time_series_table_name_list = glob.glob("*.dat")
    for target_table_name in time_series_table_name_list:
        name_list = target_table_name.split("_")
        ref_ra = float(name_list[1])
        subname_list = name_list[2].split(".dat")
        ref_dec = float(subname_list[0])
        # if the new observation locate within the tolarence, count it!
        if ref_ra - tolerance < ra and ref_ra + tolerance > ra and ref_dec - tolerance < dec and ref_dec + tolerance > dec:
            return 0, target_table_name
    return 1, None

# The def test if this observation is saved
# 0 means not yet.
# 1 means saved already.
def check_duplicate(target, target_table_name):
    # Load table
    target_table = np.loadtxt(target_table_name, dtype = object, skiprows = 1)
    JD = target[-3]
    try:
        ref_JD = target_table[24]
        if ref_JD == JD:
            return 1
    except:
        ref_JD_list = target_table[:,24]
        for ref_JD in ref_JD_list:
            if ref_JD == JD:
                return 1
    return 0

# The def append all new observed data to target light curve list.
def make_light_curve_table(inp_table, tolerance):
    workdir = os.getcwd()
    path_of_table = "{0}/time_series_table".format(TAT_env.path_of_result)
    os.system("mkdir -p {0}".format(path_of_table))
    os.chdir(path_of_table)
    print "The number of targets in queue: {0}".format(len(inp_table))
    for target in inp_table:
        # Initialize
        failure = 0
        target_table_name = None
        # If the target is detected in the past, if not , creat a new one.
        failure, target_table_name = match_names(target, tolerance) 
        if failure:
            column_names = TAT_env.titles_for_target_on_frame_table
            temp_new_table = np.array([target])
            temp_new_table = np.insert(temp_new_table, 0, column_names, axis=0)
            target_table_name = target[1]
            np.savetxt("{0}.dat".format(target_table_name), temp_new_table, fmt="%s")
        # IF this observation is saved.
        else:
            # Check if it is saved or not.
            saved = 0
            saved = check_duplicate(target, target_table_name)
            if saved == 0:
            # If not, append this observation into the target table.
                target_table = np.loadtxt(target_table_name, dtype = object)
                target_table = np.insert(target_table, len(target_table), target, axis = 0)
                np.savetxt(target_table_name, target_table, fmt = '%s')
    os.chdir(workdir)

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print "Wrong numbers of arguments"
        print "Usage: update_time_series_tables.py [table list]"
        exit(1)
    list_name = argv[1]
    table_list = np.loadtxt(list_name, dtype = str)
    # setup the spacial tolerance
    tolerance = TAT_env.pix1/3600.0 * 5.0
    print "tolerance = {0:.4f} degree".format(tolerance)
    for table_name in table_list:
        # Load target_on_frame_table
        targets_on_frame_table = np.loadtxt(table_name, dtype = object, skiprows = 1)
        # Put data into light curve table
        tolerance = TAT_env.pix1/3600.0 * 5.0
        # Match sources
        make_light_curve_table(targets_on_frame_table, tolerance)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
