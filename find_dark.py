#!/usr/bin/python
'''
Program:
    This code is used to find darks for images
Usage: 
    find_dark.py
Editor:
    Jacob975
20180621
#################################
update log
20180621 alaph 6
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
from datetime import datetime, timedelta

def match_date(current_date, date_list):
    # comfirm the type of date and datelist is int.
    current_date = int(current_date)
    new_date_list = []
    for d in date_list:
        try :
            int(d)
        except:
            continue
        else:
            new_date_list.append(int(d))
    date_list = new_date_list
    # get all delta between two dates.
    delta_list = []
    for date in date_list:
        delta_list.append(abs(date-current_date))
    # find minimum and index of minimum.
    min_delta = min(delta_list)
    index = delta_list.index(min_delta)
    nearest_date = str(date_list[index])
    return nearest_date

def stack_mdn_method(fits_list):
    data_list = []
    for name in fits_list:
        data = pyfits.getdata(name)
        data_list.append(data)
    data_list = np.array(data_list)
    sum_fits = np.median(data_list, axis = 0)
    return sum_fits

def get_dark_to(site, exptime, date, path_of_dark):
    temp_path=os.getcwd()
    # next date
    next_date = (datetime.strptime(date, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
    # setup keywords of darks
    dark_keywords_1 = "dark{0}{1}*{2}.fit".format(site, date[2:], exptime)
    dark_keywords_2 = "dark{0}{1}*{2}.fit".format(site, next_date[2:], exptime)
    # copy files matching the keywords.
    command = "cp {0} {1} 2>/dev/null".format(dark_keywords_1, path_of_dark)
    os.system(command)
    command = "cp {0} {1} 2>/dev/null".format(dark_keywords_2, path_of_dark)
    os.system(command)
    answer = len(glob.glob("{0}/*.fit".format(path_of_dark)))
    return answer

def sub_process(path, site, date, date_list, path_of_dark, exptime):
    # find another proper date to find dark.
    nearest_date = match_date(date , date_list)
    os.chdir(nearest_date)
    os.system("pwd")
    # get dark 
    number = get_dark_to(site, exptime, nearest_date, path_of_dark)
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
    path_of_image = TAT_env.path_of_image
    temp_path = path.split(path_of_image)
    temp_path_2 = temp_path[1].split("/")
    date=temp_path_2[3]
    site = temp_path_2[1]
    # get exptime from header of one of images 
    image_list = glob.glob("*.fit")
    darkh = pyfits.getheader(image_list[0])
    exptime = int(darkh["EXPTIME"])
    #----------------------------------------
    # Go to the dir of calibrate 
    path_of_calibrate = path_of_image+"/"+site+"/calibrate"
    os.chdir(path_of_calibrate)
    # get a list of all items in calibrate
    date_list = os.listdir(path_of_calibrate)
    # find the nearest date reference to original date.
    nearest_date = match_date(date, date_list)
    # defind the dir of median dark, if it doesn't exist , create it
    path_of_dark = "{0}/{1}/calibrate/{2}/dark_{3}".format(path_of_image, site, nearest_date, exptime)
    print "path of dark is :"+path_of_dark
    if os.path.isdir(path_of_dark)==False:
        temp="mkdir -p "+path_of_dark
        os.system(temp)
    #-----------------------------------------
    # Let's find the proper dark
    number = len(glob.glob(path_of_dark)) 
    # check whether the number of dark is enough, if no, find other darks.
    while number < 10:
        number, nearest_date = sub_process(path, site, date, date_list, path_of_dark, exptime)
        if len(date_list) == 1:
            print "No enough dark found"
            exit(1)
    os.chdir(path_of_dark)
    dark_list = glob.glob('dark*.fit')
    m_dark = stack_mdn_method(dark_list)
    Median_dark_name="Median_dark_{0}_{1}.fits".format(date, exptime)
    print ("The dark name is :"+Median_dark_name)
    pyfits.writeto(Median_dark_name, m_dark, overwrite= True)
    command="cp -R {0} {1}".format(Median_dark_name, path)
    os.system(command)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
