#!/usr/bin/python
'''
Program:
    This code is used to find darks for images
Usage: 
    find_flat.py
Editor:
    Jacob975
20180621
#################################
update log
20180621 alaph 1
    1. The code work 
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
import glob
import time
import fnmatch
import TAT_env
import datetime
from find_dark import match_date, stack_mdn_method

def get_flat_to(band, telescope, flat_exptime, date, path_of_flat):
    temp_path=os.getcwd()
    dark_keywords = "{0}flat{1}{2}*{3}.fit".format(band, telescope, date[2:], flat_exptime)
    command = "cp {0} {1}".format(dark_keywords, path_of_flat)
    os.system(command)
    answer = len(glob.glob("{0}/*.fit".format(path_of_flat)))
    return answer

def sub_process(path, band, telescope, date, date_list, path_of_flat, exptime):
    # find another proper date to find dark.
    nearest_date = match_date(date , date_list)
    os.chdir(nearest_date)
    os.system("pwd")
    # get dark 
    number = get_flat_to(band, telescope, flat_exptime, nearest_date, path_of_flat)
    os.chdir("..")
    date_list.remove(nearest_date)
    return number, nearest_date

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    # get original path as str and list
    path=os.getcwd()
    list_path=path.split("/")
    del list_path [0]
    # get info from path
    path_of_source = TAT_env.path_of_source
    temp_path = path.split(path_of_source)
    temp_path_2 = temp_path[1].split("/")
    date=temp_path_2[3]
    telescope = temp_path_2[1]
    # get exptime and band from header of one of images 
    image_list = glob.glob("*.fit")
    darkh = pyfits.getheader(image_list[0])
    exptime = int(darkh["EXPTIME"])
    flat_exptime = find_flat_exptime()
    band = darkh["FILTER"]
    #----------------------------------------
    # Go to the dir of calibrate 
    path_of_calibrate = path_of_source+"/"+telescope+"/calibrate"
    os.chdir(path_of_calibrate)
    # get a list of all items in calibrate
    date_list = os.listdir(path_of_calibrate)
    # find the nearest date reference to original date.
    nearest_date = match_date(date, date_list)
    # defind the dir of median dark, if it doesn't exist , create it
    path_of_flat = "{0}/{1}/calibrate/{2}/{3}flat_{4}".format(path_of_source, telescope, nearest_date, band, flat_exptime)
    print "path of flat is :"+path_of_flat
    if os.path.isdir(path_of_flat)==False:
        temp="mkdir -p "+path_of_flat
        os.system(temp)
    #-----------------------------------------
    # Let's find the proper dark
    number = len(glob.glob(path_of_flat)) 
    # check whether the number of dark is enough, if no, find other darks.
    while number < 10:
        number, nearest_date = sub_process(path, band, telescope, date, date_list, path_of_flat, flat_exptime)
    os.chdir(path_of_flat)
    flat_list = glob.glob('{0}flat*.fit'.format(band))
    m_flat = stack_mdn_method(dark_list)
    # subtracted by dark
    # normalized


    Median_flat_name="Median_flat_{0}_{1}.fits".format(date, flat_exptime)
    print ("The flat name is :"+Median_flat_name)
    pyfits.writeto(Median_flat_name, m_flat, overwrite= True)
    command="cp -R {0} {1}".format(Median_flat_name, path)
    os.system(command)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
