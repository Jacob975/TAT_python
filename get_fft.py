#!/usr/bin/python
'''
Program:
This is a program to get fft fits.
Usage:
1. get_fft.py [list name]
editor Jacob975
20170720
#################################
update log

20170720 version alpha 1
    It can run properly
'''
from sys import argv
from math import pow
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

# This is used to read .tsv file
def read_tsv_file(file_name):
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

#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()
# get property from argv
list_name=argv[-1]
list_name_list = list_name.split(".")
if list_name_list[-1] == "fits" or list_name_list[-1] == "fit":
    fits_list = [list_name]
else:
    fits_list=readfile(list_name)

# do what you want.
for name in fits_list:
    data = pyfits.getdata(name)
    data_mean = np.mean(data)
    print "mean = {0}".format(data_mean)
    imAh = pyfits.getheader(name)
    data_fft = np.fft.fft2(data)
    for i in xrange(len(data_fft)):
        for j in xrange(len(data_fft[0])):
            if i > 50 or j > 50:
                data_fft[i,j] = 0
    low_pass = np.fft.ifft2(data_fft)
    low_pass_norm = np.absolute(low_pass)
    low_pass_norm_mean = np.mean(low_pass_norm)
    print "low pass norm mean = {0}".format(low_pass_norm_mean)
    low_pass_real = np.real(low_pass)
    low_pass_imag = np.imag(low_pass)
    pyfits.writeto("low_pass_norm.fits", low_pass_norm, imAh ,clobber = True)
    pyfits.writeto("low_pass_real.fits", low_pass_real,imAh ,clobber = True)
    pyfits.writeto("low_pass_imag.fits", low_pass_imag,imAh ,clobber = True)
    data_fft = np.fft.fft2(data)
    for i in xrange(len(data_fft)):
        for j in xrange(len(data_fft[0])):
            if i < 900 or j < 900:
                data_fft[i,j] = 0
    high_pass = np.fft.ifft2(data_fft)
    high_pass_norm = np.absolute(high_pass)
    high_pass_norm_mean = np.mean(high_pass_norm)
    print "high pass norm mean = {0}".format(high_pass_norm_mean)
    high_pass_real = np.real(high_pass)
    high_pass_imag = np.imag(high_pass)
    pyfits.writeto("high_pass_norm.fits", high_pass_norm,imAh ,clobber = True)
    pyfits.writeto("high_pass_real.fits", high_pass_real,imAh ,clobber = True)
    pyfits.writeto("high_pass_imag.fits", high_pass_imag,imAh ,clobber = True)
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
