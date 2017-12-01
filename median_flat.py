#!/usr/bin/python
'''
Program:
This is a program, create flat subDARK, make a median subDARK flat, and then make data of median subDARK flat become normalized.
you need alias of median_fits.
method: 
1. Choose a folder you like, which contain flat.fits 
2. $median_flat.py [header]
editor Jacob975
20170218 version alpha 1
#################################
update log

20170218 version alpha 1
    It can run properly.
'''
import os
import fnmatch
import pyfits
import numpy as np
import curvefit
import glob
from pylab import *
from sys import argv

def stack_mean_method(fits_list):
    data_list = []
    for name in fits_list:
        data = pyfits.getdata(name)
        data_list.append(data)
    data_list = np.array(data_list)
    sum_fits = np.mean(data_list, axis = 0)
    return sum_fits

header=str(argv[1])
# get path of current direction
path=os.getcwd()
list_path=path.split("/")
del list_path[0]
# get filter and expression time
filters=list_path[-1]
# get date
date=list_path[-3]
# make subDARK each flat
temp="ls "+header+"*.fit > list"
os.system(temp)
templist=os.listdir(".")
for name in templist:
    if fnmatch.fnmatch(name, "Median_dark_*"):
        curvefit.subtract_list("list", name)
# make a median flat of all subDARKed flat, which haven't been normalized.
flat_list = glob.glob("{0}*_subDARK*".format(header))
m_flat = stack_mean_method(flat_list)
median_flat_name="Median_flat_"+date+"_"+filters+".fits"
# normalize the flat
avg = np.mean(m_flat)
median_flat = np.divide(m_flat, avg)
pyfits.writeto(median_flat_name[0:-5]+'_n.fits', median_flat, clobber = True)
print median_flat_name+' OK'
