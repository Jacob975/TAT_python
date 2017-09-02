#!/usr/bin/python
'''
Program:
This is a program to control how to read and process tat data. 
Usage:
    0. Put this code with target code in the same direction.
    1. import tat_datactrl.py in the target code.
    2. enjoy this code.
editor Jacob975
20170808
#################################
update log

20170814 version alpha 1
    1.  add class tsv_editor, star_catalog_editor, row_star_catalog_comparator

20170815 version alpha 2
    1.  add class raw_star_catalog_editor
'''

import numpy as np
import pyfits
import jdcal
import matplotlib.pyplot as plt
import jdcal
import math
#---------------------------------------------------------
# Function in this section is for reading txt like data.

# This is used to read a list of fits name.
# and return a list data
def readfile(filename):
    f = open(filename, 'r')
    data = []
    for line in f.readlines():
        # skip if no data or it's a hint.
        if line == "\n" or line.startswith('#'):
            continue
        data.append(line[:-1])
    f.close
    return data

# This is used to read .tsv file
# and return a array data
def read_tsv_file(file_name):
    f = open(file_name, 'r')
    data = []
    for line in f.readlines():
        # skip if no data or it's a hint.
        if not len(line) or line.startswith('#'):
            continue
        line = line[:-1]
        line_data = np.array(line.split("\t"))
        data.append(line_data)
    f.close()
    return data

#---------------------------------------------------------
# Function in this section is for read path from setting.

def get_path(option, VERBOSE = 1):
        setting_file = readfile("/home/Jacob975/bin/tat_python/tat_config")
        answer = []
        start_index = setting_file.index(option)
        #print setting_file
        for i in xrange(len(setting_file)):
                if i == 0:
                        continue
                elif setting_file[start_index + i] == 'end':
                        break
                answer.append(setting_file[start_index + i])
        if VERBOSE>2:print "length of answer = {0}".format(len(answer))
        if len(answer) == 0:
                if VERBOSE>0:print "no match answer"
        if len(answer) == 1:
                return answer[0]
        else:
                return answer

#----------------------------------------------------------
# This section is for tsv data control
# This is a class for read tsv file
class tsv_editor:
    data = []
    file_name = ""
    def __init__(self, file_name):
        self.file_name = file_name
        self.data = self.read_tsv_file(file_name)
    def read_tsv_file(self, file_name):
        f = open(file_name, 'r')
        data = []
        for line in f.readlines():
            # skip if no data or it's a hint.
            if not len(line) or line.startswith('#'):
                continue
            line_data = line.split("\t")
            data.append(line_data)
        f.close()
        return data
    def set_data(file_name):
        self.file_name = file_name
        self.data = self.read_tsv_file(file_name)

# This code is for plot histgram of mag vesus number
class raw_star_catalog_editor(tsv_editor):
    # This function will plot histogram of mag vesus number of stars.
    def hist(self, data, centr = 10, half_width = 5, shift = 0):
        bin_length = half_width*8
        numbers, bin_edges, patches = plt.hist(data, bins= bin_length, range = [centr - half_width + shift , centr + half_width + shift], normed = False)
        bin_middles = 0.5*(bin_edges[1:] + bin_edges[:-1])
        return bin_middles, numbers
    def hist_plot(self, title, VERBOSE = 0):
        #------------------------------
        # grab data section
        data = self.data
        # find index of title
        title_index = data[0].index(title)
        # read selected data
        mag_data = [column[title_index] for column in data]
        # do histogram
        mag_array = np.array(mag_data[2:], dtype = float)
        x_plt, y_plt = self.hist(mag_array)
        max_num_in_mag = x_plt[np.argmax(y_plt)]
        if VERBOSE>0:print "most stars within {0} mag region".format(max_num_in_mag)
        #------------------------------
        # plot section
        fig = plt.figure("Histogram of {0} in {1}".format(title, self.file_name))
        plt.title("Histogram of {0} in {1}".format(title, self.file_name))
        plt.xlabel("{0}({1})".format(mag_data[0], mag_data[1]))
        plt.yscale("log")
        plt.ylabel("number(log10(count))")
        plt.bar(x_plt, y_plt, width = 0.25)
        fig.show()

# This code is for plot difference of selected property
class raw_star_catalog_comparator(tsv_editor):
    def find_ord(self, titles, title):
        order = 0
        for element in titles:
            if element == title:
                order = titles.index(title)
        return order
    def plot(self, target, title):
        #--------------------
        # grab data section
        ref_data = self.data
        local_data = self.read_tsv_file(target)
        # find the order of the title in data and target.
        ref_order = self.find_ord(ref_data[0], title)
        local_order = self.find_ord(local_data[0], title)
        num_ref_data = ref_data[2:]
        num_local_data = local_data[2:]
        # calculate the difference between data and target.
        cmp_list = []
        for ref_star in num_ref_data:
            for local_star in num_local_data:
                ref_RA = float(ref_star[0])
                ref_DEC = float(ref_star[2])
                local_RA = float(local_star[0])
                local_DEC = float(local_star[2])
                if local_RA - 0.0007 <= ref_RA and ref_RA <= local_RA + 0.0007:
                    if local_DEC - 0.0007 <= ref_DEC and ref_DEC <= local_DEC + 0.0007:
                        ref_mag = float(ref_star[ref_order])
                        local_mag = float(local_star[local_order])
                        del_mag = local_mag - ref_mag
                        cmp_list.append([ref_mag, del_mag])
        #--------------------
        # plot section
        result_plot = plt.figure("default")
        # set text
        axes = plt.gca()
        plt.xlabel("ref_mag(magnitude)")
        plt.ylabel("local_mag - ref_mag (magnitude)")
        plt.title("{0}(ref)\n compare to \n{1}(local)".format(self.file_name, target))
        x_plot = np.array([column[0] for column in cmp_list])
        y_plot = np.array([column[1] for column in cmp_list])
        # set border of plot
        plt.plot(x_plot, y_plot, 'ro')
        y_mean = np.mean(y_plot)
        y_std = np.std(y_plot)
        axes.set_xlim([5, 20])
        axes.set_ylim([y_mean - 5*y_std, y_mean + 5*y_std])
        axes.text(6, y_mean +3*y_std, "mean of delta mag = {0:.4f}+-{1:.4f}".format(y_mean, y_std))
        plt.plot([5 , 20], [y_mean, y_mean], "-")
        plt.plot([5, 20, 20, 5], [y_mean + y_std, y_mean + y_std, y_mean - y_std, y_mean - y_std], "--")
        result_plot.show()
        return

# This code is for plot data related to time.
class star_catalog_editor(tsv_editor):
    # This is a code to mean several delta_m, and then find out the equivelent magnitude.
    def weighted_avg_and_std(self, values, weights):
        #Return the weighted average and standard deviation.
        #values, weights -- Numpy ndarrays with the same shape.
        average = np.average(values, weights=weights)
        variance = np.average((values-average)**2, weights=weights)  # Fast and numerically precise
        return average, math.sqrt(variance)
    def plot(self, y_title_list):
        #-----------------------------------------------------------------
        # grab data section
        data = self.data
        # find index of all y title, and save the title of figure.
        y_index_list = []
        figure_title = ""
        for title in y_title_list:
            figure_title += title
            figure_title += ", "
            for i in xrange(len(data[0])):
                if title == data[0][i]:
                    y_index_list.append(i)
                    break
        # find index of title "date"
        date_index = data[0].index("date")
        # convert yymmdd into Julian Date.
        date_list = [column[date_index] for column in data]
        del date_list[0]    # delete title
        del date_list[0]    # delete unit
        jd_list = []
        for date in date_list:
            yyyy = int(date[0:4])
            mm = int(date[4:6])
            dd = int(date[6:8])
            jd_list.append(sum(jdcal.gcal2jd(yyyy, mm, dd)))
        # sort data by date
        jd_array = np.array(jd_list)
        ord_index_list = np.argsort(jd_array)
        jd_array = np.sort(jd_array)
        ord_data = []
        for i in xrange(len(data)):
            if i == 0:
                ord_data.append(data[0])
                continue
            elif i == 1:
                ord_data.append(data[1])
                continue
            elif i >=2 + len(ord_index_list):
                break
            else:
                ord_data.append(data[2 + ord_index_list[i-2]])
                continue
        data = ord_data[:]
        # load y_value and y_error from data by y_index
        value_array_collection = []
        error_array_collection = []
        for i in y_index_list:
            value_array = np.array([column[i] for column in data])
            value_array_collection.append(value_array)
            error_array = np.array([column[i+1] for column in data])
            error_array_collection.append(error_array)
        value_array_collection = np.array(value_array_collection)
        error_array_collection = np.array(error_array_collection)
        #----------------------------------------------------------------
        # plot section
        result_plot = plt.figure("default")
        # set border of plot
        axes = plt.gca()
        min_jd = min(jd_list)
        max_jd = max(jd_list)
        axes.set_xlim([min_jd - 1, max_jd + 1])
        flatten_value_array_collection = value_array_collection.flatten()
        float_value_array_collection = np.array([])
        for value in flatten_value_array_collection:
            try:
                float_value_array_collection = np.append(float_value_array_collection, float(value))
            except:
                pass
        plt.xlabel("date(Julian Date)")
        plt.ylabel("{0}({1})".format(value_array_collection[0][0], value_array_collection[0][1]))
        # set title of figure
        plt.title(figure_title)
        # wipe out all non number element
        for i in xrange(len(value_array_collection)):
            temp_jd_array = np.array([])
            temp_value_array = np.array([])
            temp_error_array = np.array([])
            for j in xrange(len(jd_array)):
                try :
                    test_float = float(value_array_collection[i][2+j])
                except:
                    pass
                else:
                    temp_jd_array = np.append(temp_jd_array, jd_array[j])
                    temp_value_array = np.append(temp_value_array, float(value_array_collection[i][2+j]))
                    temp_error_array = np.append(temp_error_array, float(error_array_collection[i][2+j]))
            plt.errorbar(temp_jd_array, temp_value_array, yerr = temp_error_array, fmt = '-o')
            avg, std = self.weighted_avg_and_std(temp_value_array, temp_error_array)
            plt.plot([min_jd - 1 , max_jd + 1], [avg, avg], "-")
            plt.plot([min_jd - 1, max_jd + 1, max_jd + 1, min_jd -1], [avg + std, avg + std, avg - std, avg -std], "--")
            axes.text(min_jd, avg+2*std, "{2}: average = {0:.4f}+-{1:.4f}".format(avg, std, value_array_collection[i][0]))
            if len(value_array_collection) == 1:
                axes.set_ylim([np.mean(float_value_array_collection)-5*std, np.mean(float_value_array_collection)+5*std])
        if len(value_array_collection) > 1:
            axes.set_ylim([np.mean(float_value_array_collection)-2, np.mean(float_value_array_collection)+2])
        result_plot.show()
        return
