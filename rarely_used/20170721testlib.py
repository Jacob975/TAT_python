#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.ndimage as ndimage
import scipy.ndimage.filters as filters
import pyfits
import math
from scipy import optimize

def hist_gaussian(x, mu, sig):
    return np.power(2 * np.pi , -0.5)*np.exp(-np.power(x - mu , 2.) / (2 * np.power(sig, 2.)))/sig

def hist_gaussian_fitting(name, data, half_width = 20, shift = 0):
    # 0 : no print,
    # 1 : print answer, 
    # 2 : do graph, 
    # 3 : print debug info
    VERBOSE = 0
    # get rid of nan
    flatten_data = data[~np.isnan(data)]
    flatten_data = flatten_data[flatten_data < 100000.0]
    flatten_data = flatten_data[flatten_data > -10000.0]
    if VERBOSE>2:print len(flatten_data)
    data_mean = np.mean(flatten_data)
    if math.isnan(data_mean):
        data_mean = 0.0
    if VERBOSE>2:print data_mean
    # number is the number of star with this value
    # bin_edges is left edge position of each point on histagram.
    # patches control each rectangle's property..
    fig = plt.figure(name)
    numbers, bin_edges, patches = plt.hist(flatten_data, bins= 80, range = [data_mean - half_width + shift , data_mean + half_width + shift], normed = True)
    # find the maximum number, where will be the central of fitting figure.
    index_max = np.argmax(numbers)
    index_max = bin_edges[index_max]
    if VERBOSE>2:print "numbers: ", numbers
    bin_middles = 0.5*(bin_edges[1:] + bin_edges[:-1])
    if VERBOSE>2:print "bin_middles: ",bin_middles
    # initial paras
    if math.isnan(np.std(flatten_data)):
        std = 1.0
    else :
        std = np.std(flatten_data)
    moments = (data_mean, std)
    if VERBOSE>2:print moments
    # fit 
    paras, cov = optimize.curve_fit(hist_gaussian, bin_middles, numbers, p0 = moments)
    if VERBOSE>1:
        # draw
        x_plot = np.linspace(index_max+ half_width+ shift, index_max- half_width+ shift, 500)
        plt.plot(x_plot, hist_gaussian(x_plot, paras[0], paras[1]), 'r-', lw= 2)
        axes = plt.gca()
        axes.set_xlim([index_max-half_width+shift, index_max+half_width+shift])
        fig.show()
    if VERBOSE>0:
        print "paras: ", paras
        print "cov: \n", cov
    return paras, cov

def get_peak_filter(data, tall_limit = 10, size = 5, VERBOSE = 0):
    # get mean and noise by histgram.
    paras, cov = hist_gaussian_fitting('default', data)
    data_mean = paras[0]
    data_std = paras[1]
    # create a maximum filter and minimum filter.
    data_max = filters.maximum_filter(data, size)
    maxima = (data == data_max)
    data_min = filters.minimum_filter(data, size)
    # tall_limit * data_std + data_mean is threshold about how sensitive about this code
    diff = ((data_max - data_min) > tall_limit * data_std + data_mean)
    # maxima is a np.array, edge of shape will be set 1, others set 0.
    maxima[diff == 0] = 0
    # labeled is a np.array, denote the edge of each shape with different index numbers.
    # num_object is a number of how many different object you found.
    # example in this website: https://docs.scipy.org/doc/scipy-0.16.0/reference/generated/scipy.ndimage.measurements.label.html
    labeled, num_objects = ndimage.label(maxima)
    slices = ndimage.find_objects(labeled)
    # list up all center of shape you found.
    x, y = [], []
    for dy,dx in slices:
        x_center = (dx.start + dx.stop - 1)/2
        x.append(x_center)
        y_center = (dy.start + dy.stop - 1)/2
        y.append(y_center)
    if VERBOSE>0:
        print "number of peaks is :", len(x)
    coor = zip(y, x)
    return coor
