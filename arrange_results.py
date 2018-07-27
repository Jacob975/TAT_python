#!/usr/bin/python
'''
Program:
    This is a program for arranging results from current folder to folder in path of result. 
Usage: 
    arrange_results.py
Editor:
    Jacob975
20180727
#################################
update log
20180727 version alpha 1
    1. the code works
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import glob
import time
import TAT_env

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # define the destinate folder for results in path of reduction.
    curr_path = os.getcwd()
    reduced_curr_path = curr_path.split(TAT_env.path_of_image)
    reduced_curr_path = reduced_curr_path[1] 
    destination = TAT_env.path_of_result + reduced_curr_path
    os.system("mkdir -p {0}".format(destination))
    # Move registered images to destination.
    os.system("cp *_m.fits {0}".format(destination))
    # Move tables of targets on each frame to destination.
    os.system("cp *_m.dat {0}".format(destination))
    # Rename files in destination
    os.chdir(destination)
    os.system("rename _subDARK_divFLAT_m.dat .dat *.dat")
    os.system("rename _subDARK_divFLAT_m.fits .fits *.fits")
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
