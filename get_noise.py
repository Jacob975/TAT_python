#!/usr/bin/python
'''
Program:
This is a program the graph a plot with images of some object.
Then find the limitation magnitude of this telescope.
fitting func : y = N_{0}/t^{p} + C
variable : t
paras: N_{0}, p, C

Usage:
1. get_noise.py [stack option] [unit of noise] [list name]

stack option
    1. default : 
        mdn
    2. mdn : 
        means medien method 
        the code will find the median of each pixel on fits, then form a new image.
    3. mean :
        means mean method
        the code will find the mean of each pixel on fits, then form a new image.

unit of noise
    1. default : count 
    2. count :  Unit of noise will be count. 
    3. mag : Unit of noise will be mag.

list name
    this is a text file
    each line should contain a fits name.
    e.g.
        alpha.fits
        beta.fits
        gamma.fits

#################################
editor Jacob975
20170604 version alpha 3
#################################
update log
    20170604 version alpha 1
    This code run properly.

    20170626 version alpha 2
    1. change linear plot to log plot

    20170702 version alpha 3
    1. integrate two diff method of stack
        now we can choose one of these method below to stack our fits and find out the noise.
        medien method and mean method.
    2. upgrate the effciency of code
    3. add more details on comment for convenient.

    20170720 version alpha 4 
    1.  change save direction from 20170605_meeting to limitation_magnitude_and_noise

    20170724 version alpha 5 
    1.  add header about unit of magnitude.

    20170808 version alpha 6
    1.  use tat_config to control path of result data instead of fix the path in the code.

    20170811 version alpha 7
    1.  add comment behind imported module, used to display their topic.

    20170821 version alpha 8
    1.  Use table as datatype instead of list.
    2.  Use .fits as saved type instead of .tsv
    3.  All changes above is for control data more efficiently.
'''

import os                           # for executing linux command
import numpy as np
import matplotlib.pyplot as plt     # for plot result, the relation between time and noise
import pyfits
import time                         # for detect the lenght of processing time.
import curvefit                     # library of fitting and data processing of tat data
import tat_datactrl                 # control tat data.
from sys import argv, exit
from numpy import pi, r_, sqrt
from scipy import optimize          # for fitting func
from astropy.io import fits         # an fits file I/O module
from astropy.table import Table     # for manage data

# this func will find out noise of  all collection of some list
# then save result in noise_list
def collection( obj_list, k_factor, time_list, noise_list, method, answer_list = [], VERBOSE = 0):
    if k_factor == 0:
        exptime = 0
        noise = 0
        if VERBOSE>1:print answer_list
        if method == "mdn":
            exptime, noise = curvefit.get_noise_median_method(answer_list)
        if method == "mean":
            exptime, noise = curvefit.get_noise_mean_method(answer_list)
        if VERBOSE>0:print"time: {0}, noise: {1}".format(exptime, noise)
        time_list.append(exptime)
        noise_list.append(noise)
        return
    for i in xrange(len(obj_list)):
        sub_answer_list = answer_list[:]
        sub_answer_list.append(obj_list[i])
        sub_obj_list = obj_list[i+1:]
        collection(sub_obj_list, k_factor - 1, time_list, noise_list, method, sub_answer_list)
    return

# this func will calculate the noise of stacked fits one by one.
# If we have lots of images, this method will be efficient.
def one_by_one(fits_list, time_list, noise_list, method, VERBOSE = 0):
    for i in xrange(len(fits_list)):
        if i+1 == len(fits_list):
            continue
        sub_fits_list = fits_list[:i+1]
        if method == "mean":
            exptime, noise = curvefit.get_noise_mean_method(sub_fits_list)
        if method == "mdn":
            exptime, noise = curvefit.get_noise_median_method(sub_fits_list)
        time_list.append(exptime)
        noise_list.append(noise)
    return

# This func is used to find valid options
# if no, the first option in options list will be default one.
def choose_option(argv, options, VERBOSE = 0):
    # all options is defined in this list
    for i in xrange(len(argv)):
        if i == 0 :
            continue
        if i == len(argv) -1:
            continue
        for option in options:
            if argv[i] == option:
                if VERBOSE > 1 : print "stack option : {0}".format(option)
                return option
    if VERBOSE >1:print "Valid stack option not found,\ndefault stack option : {0}".format(options[0])
    return options[0]

# execute chosen option
def execute_option(fits_list, method, noise_unit, VERBOSE = 0):
    time_list = []
    noise_list = []
    paras = []
    cov = []
    success = 0
    if len(fits_list) < 8:
        for i in xrange(len(fits_list)):
            if VERBOSE>0:print "collection: {0}".format(i+1) 
            collection(fits_list, i+1, time_list, noise_list, method) 
        if VERBOSE>0:print "collection: done"
    else :
        one_by_one(fits_list, time_list, noise_list, method)
    time_list = np.array(time_list)
    noise_list = np.array(noise_list)
    # write down data andfitting 
    if noise_unit == "count":
        try : 
            paras, cov = pow_fitting(time_list, noise_list)
        except:
            print "fitting fail"
            paras = 0
            cov = 0
        else:
            success = 1
    elif noise_unit == "mag": 
        try :
            noise_list = -2.5 * np.log10(noise_list) - 2.5 *np.log10(3)
            paras, cov = pow_fitting_mag(time_list, noise_list)
        except:
            print "fitting fail"
            paras = 0
            cov = 0
        else:
            success = 1
    return time_list, noise_list, paras, cov, success
#---------------------------------------------------
# fitting function in count unit
def pow_function(x, base, const, pow_):
    return base/np.power(x, pow_) + const

# initial value of fitting for pow_function in count unit
def moment_pow_fitting(x_plt, value):
    const = value[-1]
    pow_ = 0.5 
    base = (value[0] - const)/np.pow(x_plt[0], p)
    return (base, const, pow_)

# fitting
def pow_fitting(x_plt, value):
    moment = moment_pow_fitting(x_plt, value)
    paras, cov = optimize.curve_fit(pow_function, x_plt, value, p0 = moment)
    return paras, cov
#----------------------------------------------------
# fitting function in mag unit
def pow_function_mag(x, amp, const):
    return amp * np.log10(x) + const

# initial value of fitting for pow_function in mag unit
def moment_pow_fitting_mag(x_plt, value):
    const = value[0]
    amp = (value[0] - value[-1])/(np.log10(x_plt[0]) - np.log10(x_plt[-1]))
    return (amp, const)

# fitting
def pow_fitting_mag(x_plt, value):
    moment = moment_pow_fitting_mag(x_plt, value)
    paras, cov = optimize.curve_fit(pow_function_mag, x_plt, value, p0 = moment)
    return paras, cov

#--------------------------------------------
# main code
# measure times
start_time = time.time()
# get all names of fits
# VERBOSE = 0 : no print
# VERBOSE = 1 : print essential data
# VERBOSE = 2 : do graph
# VERBOSE = 3 : print debug info
VERBOSE = 2
if len(argv) == 1:
    print "Usage: get_noise.py [stack option] [unit of noise] [list name]"
    exit(0)
if VERBOSE>0:print "get_noise.py start"
# get info from argv, below are options
stack_option = ["mdn", "mean"]
noise_unit_option = ["count", "mag"]
# find valid stack option in argv
method = choose_option(argv, stack_option)
if VERBOSE>0:print "method: {0}".format(method)
# find valid noise unit option in argv
noise_unit = choose_option(argv, noise_unit_option)
if VERBOSE>0:print "noise_unit: {0}".format(noise_unit)
# get name of list which contains the name of fits
list_name=argv[-1]

# read fits name from list
fits_list=tat_datactrl.readfile(list_name)

# get property of images from path
data_list = np.array([])
path = os.getcwd()
list_path = path.split("/")
scope_name = list_path[-5]
date_name = list_path[-3]
obj_name = list_path[-2]
filter_name = list_path[-1]

# setup the path of saves
path_of_result = tat_datactrl.get_path("path_of_result")
result_data_name = "{7}/limitation_magnitude_and_noise/{0}_{1}_{2}_{3}_{4}_{5}_{6}_N_to_t.fits".format(obj_name, filter_name, date_name, scope_name, method, noise_unit, list_name, path_of_result)
result_fig_name = "{7}/limitation_magnitude_and_noise/{0}_{1}_{2}_{3}_{4}_{5}_{6}_N_to_t.png".format(obj_name, filter_name, date_name, scope_name, method, noise_unit, list_name, path_of_result)
short_result_name = "{0}_{1}_{2}_{3}_{4}_{5}_{6}_N_to_t.fits".format(obj_name, filter_name, date_name, scope_name, method, noise_unit, list_name)
path_of_noise_to_some = "{0}/limitation_magnitude_and_noise/noise_in_{1}.fits".format(path_of_result, noise_unit)
fitting_func = ""
title = ('')
unit = []
if noise_unit == "count":
    fitting_func = "noise = base/np.power(exptime, pow_) + const"
    title = ('exptime', 'noise')
    unit = ['sec', 'count per sec']
if noise_unit == "mag":
    fitting_func = "noise = amp*log_10(exptime) + const"
    title = ('exptime', 'mag')
    unit = ['sec', 'mag per sec']
#-------------------------------------
# execute the options and fitting 
x_plt, noise_plt, paras, cov, success = execute_option(fits_list, method, noise_unit, VERBOSE)
result_table = Table([x_plt, noise_plt], names = title)
for i in xrange(len(title)):
    result_table[title[i]].unit = unit[i]
result_table.write(result_data_name, overwrite = True)
result_table.write(short_result_name, overwrite = True)
#---------------------------------
# write down result
head_info = [obj_name, filter_name, date_name, scope_name, method, list_name, "yes", fitting_func]
# full form :"RAWDATANAME", "FILTER", "DATE", "SCOPE", "STACK_METHOD", "LISTNAME", "NORMALIZED_NOISE", "FITTINGFUNCTION"
head_info_name = ["RAWDATA", "FILTER", "DATE", "SCOPE", "METHOD", "LIST", "NORM_N", "FFUNC"]
for i in xrange(len(head_info_name)):
    fits.setval(result_data_name, head_info_name[i], value = head_info[i])
data_name = np.array([])
data = np.array([])
type_list = np.array([])
if noise_unit == "count" and success != 0:
    value_name = ['BASE', 'CONST', 'POW_']
    values = [paras[0], paras[1], paras[2]]
    error = [sqrt(cov[0][0]), sqrt(cov[1][1]), sqrt(cov[2][2])]
    for i in xrange(len(values)):
        fits.setval(result_data_name, "{0}".format(value_name[i]), value = values[i])
        fits.setval(result_data_name, "E_{0}".format(value_name[i]), value = error[i])
    if VERBOSE>1:
        print "base: ", paras[0], "const: ", paras[1], "pow_: ", paras[2]
    data_name = np.array(['target', 'scope','band', 'date', 'method', 'list_name', 'base', 'e_base', 'const', 'e_const', 'pow_', 'e_pow_'])
    sub_units = np.array(['no unit', 'no unit', 'no unit', 'yyyymmdd', 'no unit', 'no unit', 'count per sec', 'count per sec', 'count per sec', 'count per sec', 'count per sec', 'count per sec'])
    data = np.array([obj_name, scope_name, filter_name, date_name, method, list_name, paras[0], error[0], paras[1], error[1], paras[2], error[2]])
elif noise_unit == "mag" and success != 0:
    value_name = ['AMP', 'CONST']
    values = [paras[0], paras[1]]
    error = [sqrt(cov[0][0]), sqrt(cov[1][1])]
    for i in xrange(len(values)):
        fits.setval(result_data_name, "{0}".format(value_name[i]), value = values[i])
        fits.setval(result_data_name, "E_{0}".format(value_name[i]), value = error[i])
    if VERBOSE>1:print "amp: ", paras[0], "const: ", paras[1]
    data_name = np.array(['object', 'scope', 'band', 'date', 'method', 'list_name', 'amp', 'e_amp', 'const', 'e_const'])
    sub_units = np.array(['no unit', 'no unit', 'no unit', 'yyyymmdd', 'no unit', 'no unit', 'mag per sec', 'mag per sec', 'mag per sec', 'mag per sec'])
    data = np.array([obj_name, scope_name, filter_name, date_name, method, list_name, paras[0], error[0], paras[1], error[1]])
# save result in collection database
try:
    pre_table = Table.read(path_of_noise_to_some)
    pre_table.add_row(data)
    pre_table.write(path_of_noise_to_some, overwrite = True)
    hdulist = fits.open(path_of_noise_to_some, mode = 'update')
    prihdr = hdulist[0].header
    prihdr['fitting_function'] = 'y : amp * log_10(exptime) + const'
    hdulist.flush()
    hdulist.close()
except:
    sub_table = Table(rows = [data], names = data_name)
    for i in xrange(len(data)):
        sub_table[data_name[i]].unit = sub_units[i]
    sub_table.write(path_of_noise_to_some)
    hdulist = fits.open(path_of_noise_to_some, mode = 'update')
    prihdr = hdulist[0].header
    prihdr['fitting_function'] = 'y : amp * log_10(exptime) + const'
    hdulist.flush()
    hdulist.close()
#---------------------------------
# draw limitation magnitude to time plot
result_plt = plt.figure("V_"+scope_name+" "+date_name+" "+obj_name+" "+filter_name+" "+" result")
plt.plot(x_plt, noise_plt, 'ro')
x_plt_ref = np.linspace(0, x_plt[-1], len(x_plt)*10)
if noise_unit == "count":
    if success != 0:
        plt.plot(x_plt_ref, pow_function(x_plt_ref, paras[0], paras[1], paras[2]), 'r-', lw= 2)
        plt.text(x_plt[0], noise_plt[0]-0.03, u'formula: count = base * t^{pow_} + const')
        plt.text(x_plt[0], noise_plt[0]-0.05, u'base = {0:.2f}, const = {1:.2f}, pow_ = {2:.2f}'.format(paras[0], paras[1], paras[2] ))
    axes = plt.gca()
    axes.set_xlim([x_plt[0]/2.0,x_plt[-1]*2.0])
    axes.set_ylim([noise_plt[-1]-0.1,noise_plt[0]+0.1])
    plt.xscale('log')
    plt.xlabel("time (sec)")
    plt.yscale('log')
    plt.ylabel("noise (count)")
elif noise_unit == "mag":
    if success != 0:
        plt.plot(x_plt_ref, pow_function_mag(x_plt_ref, paras[0], paras[1]), 'r-', lw= 2)
        plt.text(x_plt[0], noise_plt[-1]-0.1, u'formula: lim_mag = amp * log10(t) + const\namp = {0:.4f}+-{1}\nconst = {2:.4f}+-{3}'.format(paras[0], cov[0][0], paras[1], cov[1][1]))
    axes = plt.gca()
    axes.set_xlim([x_plt[0]/2.0,x_plt[-1]*2.0])
    axes.set_ylim([noise_plt[0]-0.1,noise_plt[-1]+0.1])
    plt.title('')
    plt.xscale('log')
    plt.xlabel("time (sec)")
    plt.ylabel("Noise equivalent magnitude (instrument mag)")
# save figure in /home/Jacob975/demo/limitation_magnitude_and_noise
plt.savefig(result_fig_name)

if VERBOSE>1:
    result_plt.show()
    raw_input()
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
