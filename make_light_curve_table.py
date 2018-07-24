#!/usr/bin/python
'''
Program:
    This is a program for convert target on frames table to target light curve table 
Usage: 
    make_light_curve_table.py [input table]
Editor:
    Jacob975
20180723
#################################
update log
20180723 version alpha 1
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
    ra = float(target[4])
    dec = float(target[5])
    target_table_list = glob.glob("*.dat")
    for target_table in target_table_list:
        name_list = target_table.split("_")
        ref_ra = float(name_list[1])
        subname_list = name_list[2].split(".")
        ref_dec = float(subname_list[0])
        # if the new observation locate within the tolarence, count it!
        if ref_ra - tolerance < ra and ref_ra + tolerance > ra and ref_dec - tolerance < dec and ref_dec + tolerance > dec:
            return 0, target_table
    return 1, None

# The def test if this observation is saved
# 0 means not yet.
# 1 means saved already.
def check_duplicate(target, target_table_name):
    # Load table
    print target_table_name
    target_table = np.loadtxt(target_table_name, dtype = object, skiprows = 1)
    date = target[20]
    location = np.where(target_table == date)
    if len(location) == 0:
        return 1
    return 0

# The def append all new observed data to target light curve list.
def Make_light_curve_table(inp_table, tolerance):
    workdir = os.getcwd()
    os.chdir(TAT_env.path_of_table)
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
        failure = 0
        failure = check_duplicate(target, "{0}.dat".format(target_table_name))
        if failure:
            continue
        # append target observation into the target table.
        else:
            target_table = np.loadtxt("{0}.dat".format(target_table_name), dtype = object)
            target_table = np.insert(target_table, len(target_table), target, axis = 0)
            np.savetxt("{0}.dat".format(target_table_name), target_table, fmt = '%s')
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
        print "Usage: make_list_curve_table.py [input table]"
        exit(1)
    table_name = argv[1]
    # Load target_on_frame_table
    targets_on_frame_table = np.loadtxt(table_name, dtype = object, skiprows = 1)
    # Put data into light curve table
    error = TAT_env.pix1/3600.0 * 5.0
    # Match sources
    Make_light_curve_table(targets_on_frame_table, tolerance = error)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
