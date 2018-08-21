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
from mysqlio_lib import save2sql, load_from_sql, show_tables

# The def find the match name of target names.
def match_names(target, tolerance, db_name):
    index_RA = TAT_env.table_titles.index("RA")
    index_DEC = TAT_env.table_titles.index("`DEC`")
    ra = float(target[index_RA])
    dec = float(target[index_DEC])
    time_series_table_name_list = show_tables(db_name)
    for target_table_name in time_series_table_name_list:
        name_list = target_table_name.split("_")
        ref_ra  = float(name_list[1])
        ref_dec = float(name_list[2])
        # if the new observation locate within the tolarence, count it!
        if ref_ra - tolerance < ra and ref_ra + tolerance > ra and ref_dec - tolerance < dec and ref_dec + tolerance > dec:
            return 0, target_table_name
    return 1, None

# The def append all new observed data to target light curve list.
def make_light_curve_table(inp_table, tolerance):
    print "The number of targets in queue: {0}".format(len(inp_table))
    time_series_db_name = TAT_env.time_series_db_name
    for target in inp_table:
        failure, target_table_name = match_names(target, tolerance, time_series_db_name) 
        if failure:
            target_table_name = target[1]
        save2sql(time_series_db_name, target_table_name, [target], unique_jd = True)

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
    frame_db_name = TAT_env.frame_db_name
    # setup the spacial tolerance
    tolerance = TAT_env.pix1/3600.0 * 5.0
    print "tolerance = {0:.4f} degree".format(tolerance)
    for table_name in table_list:
        # Load target_on_frame_table
        targets_on_frame_table = load_from_sql(frame_db_name, table_name)
        # Put data into light curve table
        tolerance = TAT_env.pix1/3600.0 * 5.0
        # Match sources
        make_light_curve_table(targets_on_frame_table, tolerance)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
