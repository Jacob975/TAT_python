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
'''

import os
import numpy as np
import matplotlib.pyplot as plt
import pyfits
import time
import curvefit
import tat_datactrl
from sys import argv, exit
from numpy import pi, r_
from scipy import optimize

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
            noise_list = -2.5 * np.log10(noise_list)
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

# write down header
path_of_result = tat_datactrl.get_path("result")
result_data_name = "{7}/limitation_magnitude_and_noise/{0}_{1}_{2}_{3}_{4}_{5}_{6}_N_to_t".format(obj_name, filter_name, date_name, scope_name, method, noise_unit, list_name, path_of_result)
result_fig_name = "{7}/limitation_magnitude_and_noise/{0}_{1}_{2}_{3}_{4}_{5}_{6}_N_to_t.png".format(obj_name, filter_name, date_name, scope_name, method, noise_unit, list_name, path_of_result)

result_file = open(result_data_name, "a")
result_file.write(obj_name + "_Noise_to_time\n")
result_file.write("filter: {0}\n".format(filter_name))
result_file.write("date: {0}\n".format(date_name))
result_file.write("scope: {0}\n".format(scope_name))
result_file.write("stack method: {0}\n".format(method))
result_file.write("list name: {0}\n".format(list_name))
# mention the noise has been normalize
result_file.write("normalize noise: yes")
if noise_unit == "count":
    result_file.write("fitting function: noise = base/np.power(exptime, pow_) + const\n")
    result_file.write("*************************************************************\n")
    result_file.write("exptime\t|\tnoise\n")
if noise_unit == "mag" :
    result_file.write("fitting function: noise = amp*log_10(exptime) + const\n")
    result_file.write("*************************************************************\n")
    result_file.write("exptime\t|\tmag\n")
result_file.write("-------------------------------------------------------------\n")

#-------------------------------------

# execute the options and fitting 
x_plt, noise_plt, paras, cov, success = execute_option(fits_list, method, noise_unit, VERBOSE)
for i in xrange(len(x_plt)):
    result_file.write("{0}\t{1}\n".format(x_plt[i],noise_plt[i]))
#---------------------------------
# write down result

result_file.write("***************************************************************\n")
if noise_unit == "count" and success != 0:
    result_file.write("base: {0:.2f}+-{3:.2f}\nconst: {1:.2f}+-{4:.2f}\npow_: {2:.3f}+-{5:.3f}\n".format(paras[0], paras[1], paras[2], cov[0][0], cov[1][1], cov[2][2]))
    result_file.close()
    result_file = open("{0}/limitation_magnitude_and_noise/noise_in_count.tsv".format(path_of_result), "a")
    result_file.write("{6}\t{11}\t{7}\t{8}\t{9}\t{10}\t{0:.2f}\t{3:.2f}\t{1:.2f}\t{4:.2f}\t{2:.3f}\t{5:.3f}\n".format(paras[0], paras[1], paras[2], cov[0][0], cov[1][1], cov[2][2], obj_name, filter_name, date_name, method, list_name, scope_name))
    result_file.close()
    if VERBOSE>1:print "base: ", paras[0], "const: ", paras[1], "pow_: ", paras[2]

elif noise_unit == "mag" and success != 0:
    result_file.write("amp: {0:.2f}+-{2:.2f}\nconst: {1:.2f}+-{3:.2f}\n".format(paras[0], paras[1], cov[0][0], cov[1][1]))
    result_file.close()
    result_file = open("{0}/limitation_magnitude_and_noise/noise_in_mag.tsv".format(path_of_result), "a")
    result_file.write("{4}\t{9}\t{5}\t{6}\t{7}\t{8}\t{0:.2f}\t{2:.2f}\t{1:.2f}\t{3:.2f}\n".format(paras[0], paras[1], cov[0][0], cov[1][1], obj_name, filter_name, date_name, method, list_name, scope_name))
    result_file.close()
    if VERBOSE>1:print "amp: ", paras[0], "const: ", paras[1]

#---------------------------------
# draw
result_plt = plt.figure(scope_name+" "+date_name+" "+obj_name+" "+filter_name+" "+" result")
plt.plot(x_plt, noise_plt, 'ro')
x_plt_ref = np.linspace(0, x_plt[-1], len(x_plt)*10)
if noise_unit == "count":
    if success != 0:
        plt.plot(x_plt_ref, pow_function(x_plt_ref, paras[0], paras[1], paras[2]), 'r-', lw= 2)
        plt.text(x_plt[0], noise_plt[0]-0.03, u'formula: count = base * t^{pow_} + const')
        plt.text(x_plt[0], noise_plt[0]-0.05, u'base = {0:.2f}, const = {1:.2f}, pow_ = {2:.2f}'.format(paras[0], paras[1], paras[2] ))
    axes = plt.gca()
    axes.set_xlim([x_plt[0],x_plt[-1]])
    axes.set_ylim([noise_plt[-1],noise_plt[0]])
    plt.xscale('log')
    plt.xlabel("time (sec)")
    plt.yscale('log')
    plt.ylabel("noise (count)")
elif noise_unit == "mag":
    if success != 0:
        plt.plot(x_plt_ref, pow_function_mag(x_plt_ref, paras[0], paras[1]), 'r-', lw= 2)
        plt.text(x_plt[0]*1.5, noise_plt[-1]-0.03, u'formula: m = amp * log10(t) + const')
        plt.text(x_plt[0]*1.5, noise_plt[-1]-0.07, u'amp = {0:.2f}\nconst = {0:.2f}'.format(paras[0], paras[1]))
    axes = plt.gca()
    axes.set_xlim([x_plt[0],x_plt[-1]])
    axes.set_ylim([noise_plt[0],noise_plt[-1]])
    plt.xscale('log')
    plt.xlabel("time (sec)")
    plt.ylabel("noise equivilent magnitude (instrument mag)")
# save data in /home/Jacob975/demo/limitation_magnitude_and_noise
plt.savefig(result_fig_name)

if VERBOSE>1:
    result_plt.show()
    raw_input()
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
