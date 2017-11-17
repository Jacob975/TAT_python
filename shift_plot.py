#!/usr/local/bin/python
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
'''
from sys import argv
import matplotlib.pyplot as plt
import numpy as np
import pyfits
import time

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
    def __init__(self, fits_list):
        # read data from fits, and calculate the position of significant star.
        self.shift_array = self.find_shift(fits_list, self.shift_array)
        # determine the time of all
        self.term = self.find_time(fits_list)
        print fits_list[0:10]
        print fits_list[10:20]
        print fits_list[0:20]
        self.section_term = self.find_time(fits_list[0:9])
        # plot the result
        self.plot()
        raw_input()
        return
    def find_shift(self, fits_list, shift_list):
        if shift_list != None:
            print "Some thing in shift list, halt program."
            return
        shift_list = []
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
    def find_time(self, fits_list):
        # This is total observation time
        init_time = fits_list[0][-10:-4]
        init_hh = int(init_time[:2])
        init_mm = int(init_time[2:4])
        init_ss = int(init_time[4:])
        init_in_sec = 3600*init_hh + 60*init_mm +init_ss
        fin_time = fits_list[-1][-10:-4]
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
        result_plot = plt.figure("Shift")
        # set text
        axes = plt.gca()
        axes.text(-19, -17, "total observing time: {0}:{1}:{2}\nthe observation time of each color : {3}:{4}:{5}".format(self.term[0], self.term[1], self.term[2], self.section_term[0], self.section_term[1], self.section_term[2]))
        axes.text(self.shift_array[0,1], self.shift_array[0,0]+2, "The init position = ({0:.2f}, {1:.2f})".format(self.shift_array[0,1], self.shift_array[0,0]))
        axes.text(self.shift_array[-1,1], self.shift_array[-1,0]+2, "The final position = ({0:.2f}, {1:.2f})".format(self.shift_array[-1,1], self.shift_array[-1,0]))
        plt.xlabel("north positive (pixel)(DEC) ---->>>")
        plt.ylabel("west positive (pixel)(-RA) ----->>>")
        plt.title("Shift")
        array_length = len(self.shift_array)
        section_length = array_length/10 +1
        for i in xrange(len(self.shift_array)):
            init = i*10
            end = (i+1)*10
            try:
                x_plot = self.shift_array[init:end,1]
                y_plot = self.shift_array[init:edn,0]
            except:
                x_plot = self.shift_array[init:,1]
                y_plot = self.shift_array[init:,0]
            # set border of plot
            plt.plot(x_plot, y_plot, 'x')
        axes.set_xlim([-20, 20])
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
