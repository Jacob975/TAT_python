#!/usr/bin/python
'''
Program:
This is a program to graph certain data in tat star catalog.

Usage:
1.  catalog_grapher.py index_1 index_2, ... ,index_n  filename
    
    please don't choose date, band, scope, method, and all stdev of property as your index
    because these property have no stdev behind, which will cause some bugs.

index:
    which column you want to grab
    index_1 will be on x_axis
    else will be on y_axis

filename:
    which file you read.
    It should generate by get_all_star.py or build_catalog.py

editor Jacob975
20170810
#################################
update log

20170810 version alpha 1
    It run properly.
'''
from sys import argv
import matplotlib.pyplot as plt
import numpy as np
import pyfits
import time
import tat_datactrl
import jdcal
import math

# This is a code to mean several delta_m, and then find out the equivelent magnitude.
def weighted_avg_and_std(values, weights):
    #Return the weighted average and standard deviation.
    #values, weights -- Numpy ndarrays with the same shape.
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)  # Fast and numerically precise
    return average, math.sqrt(variance)

# This class is for operate star catalog as a table
class star_catalog_editor:
    data = []
    def __init__(self, file_name):
        self.data = tat_datactrl.read_tsv_file(file_name)
    def read_tsv(self, file_name):
        self.data = tat_datactrl.read_tsv_file(file_name)
        return
    def test(self):
        temp_list = self.data[2]
        for element in temp_list:
            print "{0}, {1}".format(temp_list.index(element), element)
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
            elif i >=len(ord_index_list):
                break
            else:
                ord_data.append(data[2+ord_index_list[i]])
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
            avg, std = weighted_avg_and_std(temp_value_array, temp_error_array)
            plt.plot([min_jd - 1 , max_jd + 1], [avg, avg], "-")
            plt.plot([min_jd - 1, max_jd + 1, max_jd + 1, min_jd -1], [avg + std, avg + std, avg - std, avg -std], "--")
            axes.text(min_jd, avg+2*std, "{2}: average = {0:.4f}+-{1:.4f}".format(avg, std, value_array_collection[i][0]))
            if len(value_array_collection) == 1:
                axes.set_ylim([np.mean(float_value_array_collection)-5*std, np.mean(float_value_array_collection)+5*std])
        if len(value_array_collection) > 1:
            axes.set_ylim([np.mean(float_value_array_collection)-2, np.mean(float_value_array_collection)+2])
        result_plot.show()
        return

class argv_controller:
    argument = []
    filename = ""
    tags = []
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        for i in xrange(len(argument)):
            if i == len(argument) -1:
                self.filename = argument[i]
            elif i == 0:
                continue
            else:
                self.tags.append(argument[i])
                continue
    def name(self):
        return self.filename
    def tag(self):
        return self.tags

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    argument = argv_controller(argv)
    # read star catalog
    catalog = star_catalog_editor(argument.name())
    # plot the result
    catalog.plot(argument.tag())
    # pause
    raw_input()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
