#!/usr/bin/python
'''
Program:
This is a function to stack fits element by element.
and save data as a fits file 

method:
fit_stack.py [stack option] [list name]

stack option
1. default : 
    mean
2. mean :   
    The code will find the mean of each pixel on fits then form a new image.
3. mdn : 
    The code will find the median of each pixel on fits then form a new image.

Name of saved data, which will generate automatically.
[scope]_[date]_[object]_[filter]_[exptime]_[sheet]_[stack method].fits

e.g. TF_20170517_Groombridge1830_N_40s_153_mdn.fits

editor Jacob975
20170515 
#################################
update log
    20170515 version alpha 1
        It can run properly
    20170604 version alpha 2
        add header file to median.fits, which ignored before.
    20170702 version alpha 3
        1. add mean stack method, now we have two kinds of methods to stack images.
            we could select one by argv, details is writed in header.
        2. Now the name of result file will add the stack option 
    20170705 version alpha 4 
        1. the code will save star list found in result fits.
            data type is .csv
    20170720 version alpha 5
        1. Change name from fit_add.py to fit_stack.py
        2. add prescription about saved file name.
'''
from sys import argv
import numpy as np
import pyfits
import time
import curvefit
import matplotlib.pyplot as plt
import os
VERBOSE = 0

def readfile(filename):
    fo = open(filename)
    answer_1 = fo.read()
    answer=answer_1.split("\n")
    fo.close()
    while (answer[-1] == "") :
        del answer[-1]
    return answer

def stack_mdn_method(fits_list):
    data_list = []
    for name in fits_list:
        data = pyfits.getdata(name)
        data_list.append(data)
    data_list = np.array(data_list)
    sum_fits = np.median(data_list, axis = 0)
    return sum_fits

def stack_mean_method(fits_list):
    data_list = []
    sum_fits = []
    for name in fits_list:
        data = pyfits.getdata(name)
        if sum_fits == []:
            sum_fits = data
            continue
        sum_fits = np.add(sum_fits, data)
    sum_fits = np.divide(sum_fits, len(fits_list))
    return sum_fits

# get property of images from path
def get_img_property():
    path = os.getcwd()
    list_path = path.split("/")
    scope_name = list_path[-5]
    date_name = list_path[-3]
    obj_name = list_path[-2]
    filter_name = list_path[-1]
    return scope_name, date_name, obj_name, filter_name

# measure times
start_time = time.time()
# get info from argv
method = argv[1]
list_name = argv[-1]
# get info from path
scope, date, obj, filter_name = get_img_property()
# get all names of fits
fits_list=readfile(list_name)
# stack option
if len(argv) == 2:
    sum_fits = stack_mean_method(fits_list)
    method = "default"
elif method == "mdn":
    sum_fits = stack_mdn_method(fits_list)
elif method == "mean" :
    sum_fits = stack_mean_method(fits_list)
else :
    print "Wrong stack option"
    print "Please choose \"mdn\" or \"mean\". "
    print "e.g. $fit_stack.py mdn list_divFLAT"
    exit(0)

data_mean, data_std = curvefit.get_mean_std(sum_fits)
# get header file 
imAh = pyfits.getheader(fits_list[0])
fit_number = len(fits_list)
# save medien fits
save_name = "{0}_{1}_{2}_{3}_{4}_{5}.fits".format(scope, date, obj, filter_name, fit_number, method)
pyfits.writeto(save_name ,sum_fits ,imAh ,clobber = True)
print "{0}, OK".format(save_name)

