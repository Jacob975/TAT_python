#!/usr/bin/python
'''
Program:
This is a program to plot the shift of each image compare to the first one 
Usage:
1. shift_plot.py [fits list]

fits list: a list contain all fits name you want to process
editor Jacob975
20171117
#################################
update log

20171117 version alpha 1:
    1. The code works well.

20171118 version alpha 2:
    1. Add a new algorithm to calculate the shift between images, name inner prod list.
'''
from sys import argv
import matplotlib.pyplot as plt
import numpy as np
import pyfits
import time
import os
from fit_move import get_match
from curvefit import get_peak_filter, get_star, hist_gaussian_fitting, get_rid_of_exotic_severe

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

class shift_calculator():
    shift_array = None
    data_list = None
    term = None
    ts = None
    properties = {"date":None, "scope":None, "object":None, "band":None}
    def __init__(self, fits_list, ts = 1):
        # ts means time section, the number of image will be group as a section.
        #-----------------
        # read data from fits, and calculate the position of significant star.
        self.ts = ts
        self.get_property()
        self.shift_array = self.find_shift_accurate(fits_list, self.shift_array)
        # determine the time of all
        self.term = self.find_time(fits_list[1:], he = True)
        self.section_term = self.find_time(fits_list[0:ts+2])
        # plot the result
        self.plot()
        raw_input()
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
    def find_shift(self, fits_list, shift_list):
        # find the shift of each image compare to the first one.
        # ----------------
        # if the process have been done before, stop the program.
        if shift_list != None:
            print "Some thing in shift list, halt program."
            return
        shift_list = []
        # take significant star, calculate the center of flux.
        for name in fits_list:
            data = pyfits.getdata(name)
            large_signal_array = np.where(data > 50000)
            value_array = data[large_signal_array]
            position = np.average(large_signal_array, weights = value_array, axis = 1)
            if VERBOSE>1:print "{0}, {1}".format(position[0], position[1])
            shift_list.append(position)
        shift_array = np.array(shift_list)
        shift_array = np.subtract(shift_array, shift_array[0])
        return shift_array
    def find_shift_accurate(self, fits_list, shift_list):
        # find the shift of each image compare to the first one.
        # ----------------
        # if the process have been done before, stop the program.
        if shift_list != None:
            print "Some thing in shift list, halt program."
            return
        shift_list = []
        # choose the first image as ref
        ref_data = pyfits.getdata(fits_list[0])
        ref_paras, ref_cov = hist_gaussian_fitting("default", ref_data)
        ref_star_list = self.get_star_list(ref_data)
        rest_fits_list = fits_list[1:]
        for name in rest_fits_list:
            data = pyfits.getdata(name)
            star_list = self.get_star_list(data)
            match_star_list, delta_x_list, delta_y_list, succeed = get_match(ref_star_list, star_list )
            # we need at least 3 stars been identified.
            if len(match_star_list) < 3:
                continue
            delta_x_list = get_rid_of_exotic_severe(delta_x_list)
            delta_y_list = get_rid_of_exotic_severe(delta_y_list)
            delta_x = np.mean(delta_x_list)
            delta_y = np.mean(delta_y_list)
            position = np.array([delta_x, delta_y])
            shift_list.append(position)
        shift_array = np.array(shift_list)
        shift_array = np.subtract(shift_array, shift_array[0])
        return shift_array
    def get_star_list(self, data, sz = 29, tl = 15, hwl = 3, ecc = 1, max_num = 30):
        # test hwo many peak in this figure.
        # If too much, raise up the limitation of size
        peak_list = []
        while len(peak_list) >500 or len(peak_list) < 3:
            sz +=1
            peak_list = get_peak_filter(data, tall_limit = tl, size = sz)
        if VERBOSE>3:
            print "peak list: "
            for peak in peak_list:
                print peak[1], peak[0]
        # test how many stars in this figure.
        # If too much, raise up the limitation of half_width with default = 4
        star_list = []
        while len(star_list) > max_num or len(star_list) < 3:
            hwl += 1
            star_list = get_star(data, peak_list, margin = 4, half_width_lmt = hwl, eccentricity = ecc)
            if VERBOSE>1:print "hwl = {0}, len of star_list = {1}".format(hwl, len(star_list))
        if VERBOSE>3:
            print "star list: "
            for star in star_list:
                print star[2], star[1]
        star_list = np.sort(star_list, order = 'xsigma')
        star_list = np.sort(star_list, order = 'ysigma')
        return star_list
    def find_time(self, fits_list, he = False):
        # This is total observation time
        init_time = fits_list[0][16:22]
        if he:
            self.init = init_time
        init_hh = int(init_time[:2])
        init_mm = int(init_time[2:4])
        init_ss = int(init_time[4:])
        init_in_sec = 3600*init_hh + 60*init_mm +init_ss
        fin_time = fits_list[-1][16:22]
        if he:
            self.fin = fin_time
        fin_hh = int(fin_time[:2])
        fin_mm = int(fin_time[2:4])
        fin_ss = int(fin_time[4:])
        fin_in_sec = 3600*fin_hh + 60*fin_mm +fin_ss
        delta_t = fin_in_sec - init_in_sec
        hh = delta_t/3600
        rest = delta_t%3600
        mm = rest/60
        rest = rest%60
        ss = rest
        term = []
        term.append(hh)
        term.append(mm)
        term.append(ss)
        return term
    def plot(self):
        #--------------------
        # plot section
        title = "Target: {0}, date: {1}, telescope:{2}, exptime of each point:{3}\nobserve from {4} to {5}.".format(self.properties["object"], self.properties["date"], self.properties["scope"], self.properties["band"], self.init, self.fin)
        result_plot = plt.figure(title)
        # set text
        axes = plt.gca()
        axes.text(-19, -17, "total observing time: {0}:{1}:{2}\nthe observation time of each color : {3}:{4}:{5}".format(self.term[0], self.term[1], self.term[2], self.section_term[0], self.section_term[1], self.section_term[2]))
        axes.text(self.shift_array[0,1], self.shift_array[0,0]+2, "The init position = ({0:.2f}, {1:.2f})".format(self.shift_array[0,1], self.shift_array[0,0]))
        axes.text(self.shift_array[-1,1], self.shift_array[-1,0]+2, "The final position = ({0:.2f}, {1:.2f})".format(self.shift_array[-1,1], self.shift_array[-1,0]))
        # determine the direction of axis
        if self.properties["scope"] == "TF":
            plt.xlabel("north positive (pixel)(DEC) ---->>>")
            plt.ylabel("east positive (pixel)(RA) ---->>>")
        elif self.properties["scope"] == "KU":
            plt.xlabel("north positive (pixel)(DEC) ---->>>")
            plt.ylabel("east positive (pixel)(RA) ---->>>")
        else :
            plt.xlabel("north positive (pixel)(DEC) ---->>>")
            plt.ylabel("west positive (pixel)(-RA) ---->>>")
        plt.title(title)
        array_length = len(self.shift_array)
        section_length = array_length/self.ts +1
        for i in xrange(len(self.shift_array)):
            init = i*self.ts
            end = (i+1)*self.ts
            try:
                x_plot = self.shift_array[init:end,1]
                y_plot = self.shift_array[init:edn,0]
            except:
                x_plot = self.shift_array[init:,1]
                y_plot = self.shift_array[init:,0]
            # set border of plot
            plt.plot(x_plot, y_plot, 'x')
        axes.set_xlim([-30, 10])
        axes.set_ylim([-20, 20])
        plt.savefig("Shift.png")
        result_plot.show()
        return

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    list_name=argv[-1]
    fits_list=readfile(list_name)
    # do what you want.
    student = shift_calculator(fits_list)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
