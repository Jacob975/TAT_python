#!/usr/bin/python
'''
Program:
    This is a program for checking dark. 
Usage: 
    check_dark_manual.py [folder name list]
Editor:
    Jacob975
20180919
#################################
update log
20180919 version alpha 1
    1. The code works
'''
import os 
import numpy as np
import glob
import time
import TAT_env
from sys import argv
from Do_Data_Reduction import check_cal

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 2:
        print "Error! the number of arguments is wrong."
        print "Usage: check_dark_manual.py [folder name list]"
        exit()
    folder_list_name = argv[1]
    #---------------------------------------
    # Load the file containing folder names.
    folder_list = np.loadtxt(folder_list_name, dtype = str)
    check_cal(folder_list, [], [], save_log = False)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
