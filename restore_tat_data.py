#!/usr/bin/python
'''
Program:
    This code is used to restore data structure
    Restoring make test easier
Usage: 
    restore.py
Editor:
    Jacob975
20180621
#################################
update log
20180621 alaph 1
    1. the code works 
'''
import os 
from glob import glob
import time
import TAT_env

#--------------------------------------------
# main code
if __name__ == "__main__":
    # measure times
    start_time = time.time()
    #----------------------------------------
    # Move images back to base directory
    command = "find . -mindepth 2 -type f -exec mv -t . '{}' +"
    os.system(command)
    # Remove all sub-folder
    command = "rm -R -- */"
    os.system(command)
    # Remove synthesis files
    command = "rm list*"
    os.system(command)
    command = "rm *.fits"
    os.system(command)
    # Remove all denotation
    X_denotations = glob('X_*_X')
    for name in X_denotations:
        command = "mv {0} {1}".format(name, name[2:-2])     
        os.system(command)
    #---------------------------------------
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
