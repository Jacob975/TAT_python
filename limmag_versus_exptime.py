#!/usr/bin/python
'''
Program:
This is a program the graph a plot with images of some object.
Then find the limitation magnitude of this telescope.
fitting func : y = N_{0}/t^{p} + C
variable : t
paras: N_{0}, p, C

Usage:
1. limmag_versus_exptime.py [stack option] [unit of noise] [list name]

stack option
    1. default : 
        mean
    2. mdn : 
        means medien method 
        the code will find the median of each pixel on fits, then form a new image.
    3. mean :
        means mean method
        the code will find the mean of each pixel on fits, then form a new image.

type of noise
    1. default : rms 
    2. rms :  Unit of noise will be count. 
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

    20171127 version alpha 9
    1.  code is classified
    2. data points come with error bar.
'''

import os                           # for executing linux command
import numpy as np
import matplotlib.pyplot as plt     # for plot result, the relation between time and noise
import pyfits
import time                         # for detect the lenght of processing time.
import curvefit                     # library of fitting and data processing of tat data
import TAT_env                      # the table of environment const.
import lim_mag
import warnings
from tat_datactrl import readfile   # control tat data.
from sys import argv, exit
from numpy import pi, r_, sqrt
from scipy import optimize          # for fitting func
from astropy.io import fits         # an fits file I/O module
from astropy.table import Table     # for manage data

# VERBOSE = 0 : no print
# VERBOSE = 1 : print essential data
# VERBOSE = 2 : do graph
# VERBOSE = 3 : print debug info
VERBOSE = 2

# This class is used to manage arguments from users.
class argv_controller():
    stack_option = ["mdn", "mean"]
    stack_mod = None
    unit_option = ["rms", "mag"]
    unit = None
    list_name = None
    fits_name_list = None
    def __init__(self, argvs):
        if VERBOSE>0:print "Analyze the arguments"
        # test the form of argument is valid
        if len(argvs) <= 1:
            print "Wrong numbers of arguments"
            print "Usage: get_noise.py [stack option] [type of noise] [list name]"
            return
        # read arguments
        for i in xrange(len(argvs)):
            if self.stack_mod == None:
                self.stack_mod = self.is_this(self.stack_option, argvs[i])
            if self.unit == None: 
                self.unit = self.is_this(self.unit_option, argvs[i])
            if self.fits_name_list == None and i !=0:
                try:
                    self.fits_name_list = readfile(argvs[i])
                except:
                    pass
                else:
                    self.list_name = argvs[i]
        # check if the initialization is success or not.
        # if not, use default argument.
        if self.stack_mod == None:
            self.stack_mod = "mean"
        if self.unit == None:
            self.unit = "rms"
        if self.fits_name_list == None:
            print "Wrong content of argument"
            print "Please put the name of fits list into the argument."
        # print the options
        if VERBOSE>1:
            print "stack mod: {0}, unit: {1}".format(self.stack_mod, self.unit)
        return
    def is_this(self, options, inp):
        for element in options:
            if element == inp:
                return inp
        return None

class lim_mag_versus_time():
    # parameters
    stack_mod = "mean"
    unit = "rms"
    list_name = None
    lim_mag = None
    exptime = None
    fits_name_list = None
    fits_data_list = None
    path_of_result = None
    paras = None
    cov = None
    properties = {"date":None, "scope":None, "object":None, "band":None}
    def __init__(self, argu):
        # test the form of argument is valid
        if argu.stack_mod != None: 
            self.stack_mod = argu.stack_mod
        if argu.unit != None: 
            self.unit = argu.unit
        self.list_name = argu.list_name
        self.fits_name_list = argu.fits_name_list
        self.get_property()
        self.set_result_path()
        # compute the value versus time
        self.gene_success, rms, e_rms, exptime = self.generator(self.fits_name_list)
        self.exptime = exptime
        if not self.gene_success:
            print "generator error"
            return
        # convert the unit of value into proper one
        self.conv_success, value, e_value = self.convertor(rms, e_rms)
        if not self.conv_success:
            print "convertor error"
            return
        # fitting
        self.fit_success, paras, cov = self.fitting_manager(value, e_value, exptime)
        if not self.fit_success:
            print "fitting error"
        self.paras = paras
        self.cov = cov
        # plot
        self.plot_success = self.plotter(paras, cov, value, e_value, exptime) 
        if not self.plot_success:
            print "plotter error"
        self.t_con_success = self.table_constructor(value, e_value, exptime)
        self.save_success = self.save()
        return
    def generator(self, fits_name_list):
        # This func is used to generate all answers of lim_mag versus exptime.
        success = 0
        rms_list = []
        e_rms_list = []
        exptime_list = []
        if len(fits_name_list) < 10:
            for i in xrange(len(fits_name_list)):
                temp_exptime_list = []
                temp_rms_list = []
                if VERBOSE>0:print "combinator: {0}".format(i+1)
                # calculation
                combinator(fits_name_list, i+1, temp_exptime_list, temp_rms_list, self.stack_mod)
                # do mean and std over data
                temp_rms_array = np.array(temp_rms_list)
                rms = np.mean(temp_rms_array)
                e_rms = np.std(temp_rms_array)
                temp_exptime_array = np.array(temp_exptime_list)
                exptime = temp_exptime_array[0]
                #append result to answer list
                rms_list.append(rms)
                e_rms_list.append(e_rms)
                exptime_list.append(exptime)
            if len(rms_list) > 1 and len(exptime_list) > 1:
                success = 1
        else:
            one_by_one(fits_name_list, exptime_list, rms_list, self.stack_mod)
            e_rms_list = [1 for x in xrange(len(rms_list))]
            success = 1
        rms_array = np.array(rms_list)
        e_rms_array = np.array(e_rms_list)
        exptime_array = np.array(exptime_list)
        return success, rms_array, e_rms_array, exptime_array    
    
    def convertor(self, rms_array, e_rms_array):
        # this is used to convert the unit of answer to the unit you desire.
        success = 0
        if self.unit == "rms":
            success = 1
            return success, rms_array, e_rms_array
        elif self.unit == "mag":
            # convert noise into limitin magnitude by inst mag
            noise_eq_inst_mag_array = -2.5 * np.log10(np.multiply(rms_array, 3))
            rms_add_e_rms_array = rms_array + e_rms_array
            e_noise_eq_inst_mag_array = +2.5 * np.log10(np.multiply(rms_add_e_rms_array, 3)) - 2.5 * np.log10(np.multiply(rms_array, 3))
            # find the delta mag
            warnings.filterwarnings("ignore")
            scope = self.properties["scope"]
            date = self.properties["date"]
            obj = self.properties["object"]
            band = self.properties["band"][0]
            stack_mod = self.stack_mod
            temp_argv = [scope, date, obj, band, stack_mod, self.exptime[0]]
            properties = lim_mag.argv_controller(temp_argv, VERBOSE = 2)
            path_of_del_m = TAT_env.path_of_result + "/limitation_magnitude_and_noise/delta_mag.fits"
            path_of_inst_m = TAT_env.path_of_result + "/limitation_magnitude_and_noise/noise_in_mag.fits"
            magnitude = lim_mag.fits_table_reader(path_of_del_m, path_of_inst_m)
            del_mag = float(magnitude.quest_del_mag(properties.keywords, self.exptime[0], VERBOSE))
            if VERBOSE>0: print del_mag
            noise_eq_lim_mag_array = noise_eq_inst_mag_array - del_mag
            e_noise_eq_lim_mag_array = e_noise_eq_inst_mag_array
            success = 1
        return success, noise_eq_lim_mag_array, e_noise_eq_lim_mag_array

    def fitting_manager(self, value_list, e_value_list, exptime_list):
        # this is used to fitting answer list with certain noise-time relation function, different by unit.
        success = 0
        if self.unit == "rms":
            try :
                paras, cov = pow_fitting(exptime_list[:-1], value_list[:-1], e_value_list[:-1])
                self.fitting_func = "rms = base * t^(pow_) + const"
            except:
                print "fitting fail"
                paras = None
                cov = None
            else:
                success = 1
            return
        if self.unit == "mag":
            try:
                paras, cov = pow_fitting_mag(exptime_list[:-1], value_list[:-1], e_value_list[:-1])
                self.fitting_func = "lim_mag = amp * log10(t) + const"
            except:
                print "fitting fail"
                paras = None
                cov = None
            else:
                success = 1
        return success, paras, cov

    def plotter(self, paras, cov, value, e_value, exptime):
        # This is used to plot the answer and fitting curve.
        #---------------------------------
        # draw the noise versus exptime
        result_plt = plt.figure("The limiting magnitude of images from {0}_{1}_{2}_{3} with {4} slides".format(self.properties["scope"], self.properties["object"], self.properties["date"], self.properties["band"], len(self.fits_name_list)))
        x_plt = exptime
        noise_plt = value
        weight_n = e_value
        plt.errorbar(x_plt, noise_plt, yerr = weight_n, fmt = 'ro')
        x_plt_ref = np.linspace(0, x_plt[-1], len(x_plt)*10)
        if self.unit == "count":
            if self.fit_success != 0:
                plt.plot(x_plt_ref, pow_function(x_plt_ref, paras[0], paras[1], paras[2]), 'r-', lw= 2)
                plt.text(x_plt[0], noise_plt[0]-0.03, u'formula: {0}'.format(self.fitting_func))
                plt.text(x_plt[0], noise_plt[0]-0.05, u'base = {0:.2f}, const = {1:.2f}, pow_ = {2:.2f}'.format(paras[0], paras[1], paras[2] ))
            axes = plt.gca()
            axes.set_xlim([x_plt[0]/2.0,x_plt[-1]*2.0])
            axes.set_ylim([noise_plt[-1]-0.1,noise_plt[0]+0.1])
            plt.xscale('log')
            plt.xlabel("time (sec)")
            plt.yscale('log')
            plt.ylabel("noise (count)")
        elif self.unit == "mag":
            if self.fit_success != 0:
                plt.plot(x_plt_ref, pow_function_mag(x_plt_ref, paras[0], paras[1]), 'r-', lw= 2)
                plt.text(x_plt[0], noise_plt[-1]-0.1, u'formula: {4}\namp = {0:.4f}+-{1}\nconst = {2:.4f}+-{3}'.format(paras[0], sqrt(cov[0][0]), paras[1], sqrt(cov[1][1]), self.fitting_func))
            axes = plt.gca()
            axes.set_xlim([x_plt[0]/2.0,x_plt[-1]*2.0])
            axes.set_ylim([noise_plt[0]-0.1,noise_plt[-1]+0.1])
            plt.title('')
            plt.xscale('log')
            plt.xlabel("time (sec)")
            plt.ylabel("limiting magnitude(Pmag)")
        success = 1
        if VERBOSE>1:result_plt.show()
        # save figure in /home/Jacob975/demo/limitation_magnitude_and_noise
        plt.savefig(self.result_fig_name)
        return success
    def save(self):
        os.system("cp {0} {1}".format(self.short_result_name, self.result_data_name))
        return
    def get_property(self):
        # get property of images from path
        path = os.getcwd()
        list_path = path.split("/")
        self.properties["scope"] = list_path[-5]
        self.properties["date"] = list_path[-3]
        self.properties["object"] = list_path[-2]
        self.properties["band"] = list_path[-1]
        return
    def set_result_path(self):
        # setup the path of saves
        path_of_result = TAT_env.path_of_result
        scope = self.properties["scope"]
        date = self.properties["date"]
        obj = self.properties["object"]
        band = self.properties["band"]
        unit = self.unit
        stack_mod = self.stack_mod
        list_name = self.list_name
        # belows are useful path we set
        self.short_result_name = "{0}_{1}_{2}_{3}_{4}_{5}_{6}_limmag_to_t.fits".format(obj, band, date, scope, stack_mod, unit, list_name)
        self.result_data_name = "{1}/lim_mag_versus_exptime/{0}".format(self.short_result_name, path_of_result)
        self.result_fig_name = "{1}/lim_mag_versus_exptime/{0}.png".format(self.short_result_name[:-5], path_of_result)
        self.path_of_noise_to_some = "{0}/lim_mag_versus_exptime/noise_in_{1}.fits".format(path_of_result, unit)
        return
    def table_constructor(self, y, y_err, exptime):
        success =0
        paras = self.paras
        cov = self.cov
        # init the table with unit
        if self.unit == "rms":
            title = ["exptime", "rms", "e_rms"]
            unit_title = ["sec", "count", "count"]
        if self.unit == "mag":
            title = ["exptime", "lim_mag", "e_lim_mag"]
            unit_title = ["sec", "mag", "mag"]
        # set the table of result
        result_table = Table([exptime, y, y_err], names = title)
        for i in xrange(len(title)):
            result_table[title[i]].unit = unit_title[i]
        # save table
        result_table.write(self.short_result_name, overwrite = True)
        #---------------------------------
        # write down result
        head_info = [self.properties["object"], self.properties["band"], self.properties["date"], self.properties["scope"], self.stack_mod, self.list_name, "yes", self.fitting_func]
        # full form :"RAWDATANAME", "FILTER", "DATE", "SCOPE", "STACK_METHOD", "LISTNAME", "NORMALIZED_NOISE", "FITTINGFUNCTION"
        head_info_name = ["RAWDATA", "FILTER", "DATE", "SCOPE", "METHOD", "LIST", "NORM_N", "FFUNC"]
        for i in xrange(len(head_info_name)):
            fits.setval(self.short_result_name, head_info_name[i], value = head_info[i])
        data_name = np.array([])
        data = np.array([])
        type_list = np.array([])
        if self.unit == "count" and self.plot_success != 0:
            para_name = ['BASE', 'CONST', 'POW_']
            parameters = [paras[0], paras[1], paras[2]]
            e_parameters = [sqrt(cov[0][0]), sqrt(cov[1][1]), sqrt(cov[2][2])]
            for i in xrange(len(parameters)):
                fits.setval(self.short_result_name, "{0}".format(para_name[i]), value = parameters[i])
                fits.setval(self.short_result_name, "E_{0}".format(para_name[i]), value = e_parameters[i])
            if VERBOSE>1:
                print "base: ", paras[0], "const: ", paras[1], "pow_: ", paras[2]
            data_name = np.array(['target', 'scope','band', 'date', 'method', 'list_name', 'base', 'e_base', 'const', 'e_const', 'pow_', 'e_pow_'])
            sub_units = np.array(['no unit', 'no unit', 'no unit', 'yyyymmdd', 'no unit', 'no unit', 'count per sec', 'count per sec', 'count per sec', 'count per sec', 'count per sec', 'count per sec'])
            data = np.array([self.properties["object"], self.properties["scope"], self.properties["band"], self.properties["date"], self.stack_mod, self.list_name, paras[0], e_parameters[0], paras[1], e_parameters[1], paras[2], e_parameters[2]])
        elif self.unit == "mag" and self.plot_success != 0:
            value_name = ['AMP', 'CONST']
            parameters = [paras[0], paras[1]]
            e_parameters = [sqrt(cov[0][0]), sqrt(cov[1][1])]
            for i in xrange(len(parameters)):
                fits.setval(self.short_result_name, "{0}".format(value_name[i]), value = parameters[i])
                fits.setval(self.short_result_name, "E_{0}".format(value_name[i]), value = e_parameters[i])
            if VERBOSE>1:print "amp: ", paras[0], "const: ", paras[1]
            data_name = np.array(['object', 'scope', 'band', 'date', 'method', 'list_name', 'amp', 'e_amp', 'const', 'e_const'])
            sub_units = np.array(['no unit', 'no unit', 'no unit', 'yyyymmdd', 'no unit', 'no unit', 'mag per sec', 'mag per sec', 'mag per sec', 'mag per sec'])
            data = np.array([self.properties["object"], self.properties["scope"], self.properties["band"], self.properties["date"], self.stack_mod, self.list_name, paras[0], e_parameters[0], paras[1], e_parameters[1]])
        # save result in combinator database
        try:
            existing_table = Table.read(self.path_of_noise_to_some)
            existing_table.add_row(data)
            existing_table.write(self.path_of_noise_to_some, overwrite = True)
            hdulist = fits.open(self.path_of_noise_to_some, mode = 'update')
            prihdr = hdulist[0].header
            prihdr['fitting_function'] = self.fitting_func
            hdulist.flush()
            hdulist.close()
            success = 1
        except:
            new_table = Table(rows = [data], names = data_name)
            for i in xrange(len(data)):
                new_table[data_name[i]].unit = sub_units[i]
            new_table.write(self.path_of_noise_to_some)
            hdulist = fits.open(self.path_of_noise_to_some, mode = 'update')
            prihdr = hdulist[0].header
            prihdr['fitting_function'] = self.fitting_func
            hdulist.flush()
            hdulist.close()
            success = 1
        return success

# this func will find out noise of  all combinator of some list
# then save result in noise_list
def combinator( obj_list, k_factor, time_list, noise_list, method, answer_list = [], VERBOSE = 0):
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
        # choose current one
        sub_answer_list.append(obj_list[i])
        # delete others before current one
        sub_obj_list = obj_list[i+1:]
        # recursive
        combinator(sub_obj_list, k_factor - 1, time_list, noise_list, method, sub_answer_list)
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
def pow_fitting(x_plt, value, e_value):
    moment = moment_pow_fitting(x_plt, value)
    paras, cov = optimize.curve_fit(pow_function, x_plt, value, p0 = moment, sigma = e_value)
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
def pow_fitting_mag(x_plt, value, e_value):
    moment = moment_pow_fitting_mag(x_plt, value)
    paras, cov = optimize.curve_fit(pow_function_mag, x_plt, value, p0 = moment, sigma = e_value)
    return paras, cov

#--------------------------------------------
# main code
if __name__ == "__main__":
    # measure times
    start_time = time.time()
    student = argv_controller(argv)
    main_process = lim_mag_versus_time(student)

# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
