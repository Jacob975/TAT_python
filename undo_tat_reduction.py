#!/usr/bin/python
'''
Program:
    This code is used to restore data structure
    Restoring make test easier
Usage: 
    undo_tat_reduction.py
Editor:
    Jacob975
20180621
#################################
update log
20180621 version alaph 1
    1. The code works 
20180625 version alpha 2
    1. The code renamed from restore_tat_data.py to flatten_tat_data.py
20180710 version alpha 3
    1. Rename from flatten_tat_data.py to undo_tat_reduction.py
'''
import os 
from glob import glob
import time
import TAT_env

def undo_tat_reduction():
    # Move images back to base directory
    command = "find . -mindepth 2 -type f -exec mv -t . '{}' +"
    os.system(command)
    # Remove all sub-folder
    command = "rm -R -- */"
    os.system(command)
    # Remove synthesis files
    command = "rm *_list* *.fits *.tar *.pro *.dat *.reg *.wcs *.new"
    os.system(command)
    # Remove all indications 
    X_denotations = glob('X_*_X')
    for name in X_denotations:
        command = "mv {0} {1}".format(name, name[2:-2])     
        os.system(command)
    return

#--------------------------------------------
# main code
if __name__ == "__main__":
    # measure times
    start_time = time.time()
    #----------------------------------------
    undo_tat_reduction()
    #---------------------------------------
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
