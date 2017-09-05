#!/usr/bin/python
'''
Program:
This is a program to graph all data in fits table. 
Usage:
1. tat_grapher.py [listname of fitsname]

Usage:
    1. tat_grapher.py some.fits              
    2. tat_grapher.py another.fits
    3. tat_grapher.py big_list          
editor Jacob975
20170901
#################################
update log

20170901 version alpha 1
    It works properly.
'''
from sys import argv
from astropy.table import Table
from numpy import sqrt
import numpy as np
import pyfits                       # fits I/O
import time                         # time controller
import tat_datactrl                 # file format I/O
import curvefit                     # fitting library
import matplotlib.pyplot as plt     # for plot result, the relation between time and lim_mag
import matplotlib
# This class is used for control argument.
class argv_controller:
    # fl means file list
    fl = []
    def __init__(self, argu):
        if len(argu) < 2:
            print "Too less arguemnt"
            print "Usage: tat_grapher.py [fitsname or listname]"
            return
        elif len(argu) > 2:
            print "Too many argument"
            print "Usage: tat_grapher.py [fitsname or listname]"
            return
        list_name = argu[-1].split('.')
        if list_name[-1] == 'fits' or list_name[-1] == 'fit':
            self.fl = [argu[-1]]
        else:
            self.fl = tat_datactrl.readfile(argu[-1])
    def fits_list(self):
        return self.fl

# This class is used to control the border of plot
class border_ctrl:
    ub = 0
    lb = 0
    def __init__(self):
        return
    def __str__(self):
        return "upperbound = {0}, lowerbound = {1}".format(self.ub, self.lb)
    # control the range of border
    def set(self, lower_bound, upper_bound):
        if self.ub == 0 and self.lb == 0:
            self.ub = upper_bound
            self.lb = lower_bound
        if upper_bound > self.ub:
            self.ub = upper_bound
        if lower_bound < self.lb:
            self.lb = lower_bound
        return 
    def upperbound(self):
        return self.ub
    def lowerbound(self):
        return self.lb

# This class is used for plot graph
class lim_mag_grapher:
    table_list = []
    fits_list = []

    # read data and graph 
    def __init__(self, fits_list):
        self.fits_list = fits_list
        self.lim_mag_plot()
        return

    # graph all data in the same plot
    def lim_mag_plot(self):
        result_fig = plt.figure("Default")
        plt.xscale('log')
        plt.xlabel("time (sec)")
        plt.ylabel("limitation magnitude (mag)")
        plt.title("fitting formula: lim_mag = amp * log10(time) + const")
        x_border = border_ctrl()
        y_border = border_ctrl()
        for name in self.fits_list:
            # setup data part
            data_table = Table.read(name)
            # read delta magnitude form fits file
            datah = pyfits.getheader(name)
            try:
                del_m = float(datah['D_MAG'])
            except:
                del_m = 0.0
            # read value and entries
            self.table_list.append(data_table)
            time_array = np.array(data_table['exptime'])
            time_array_ref = np.linspace(time_array[0]/10.0, time_array[-1]*10.0, len(time_array)*10)
            mag_array = np.array(data_table['mag']) + del_m
            # set border
            x_border.set(time_array[0], time_array[-1])
            y_border.set(mag_array[0], mag_array[-1])
            axes = plt.gca()
            axes.set_xlim([ x_border.lowerbound() / 10, x_border.upperbound() * 10])
            axes.set_ylim([ y_border.upperbound() + 0.1, y_border.lowerbound() - 1])
            # fitting by lim_mag : amp * log_10(exptime) + const
            paras, cov = curvefit.pow_fitting_mag(time_array, mag_array)
            error = sqrt(cov)
            # plot part
            plt.plot(time_array, mag_array, 'o')
            plt.plot(time_array_ref, curvefit.pow_function_mag(time_array_ref, paras[0], paras[1]), '-', lw= 1, label = "{0}, amp = {1:.4f}+-{2:.4f}, const = {3:.4f}+-{4:.4f}".format(name, paras[0], error[0][0], paras[1], error[1][1]))
            plt.legend()
            matplotlib.rcParams.update({'font.size': 8}) 
            #plt.text(time_array[0], mag_array[0], u'name: {4}\nformula: lim_mag = amp * log10(t) + const\namp = {0:.4f}+-{1}\nconst = {2:.4f}+-{3}'.format(paras[0], error[0][0], paras[1], error[1][1], name))
        plt.savefig("Default.png", dpi= 300)
        result_fig.show()
        raw_input()

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    argu = argv_controller(argv)
    # plot all data in the same picture
    result_fig = lim_mag_grapher(argu.fits_list())
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
