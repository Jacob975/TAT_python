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
from pylab import *
from sys import argv

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
command_line="median_fits "+header+"*_subDARK"
os.system(command_line)

median_flat_name="Median_flat_"+date+"_"+filters+".fits"
temp="mv Median_"+header+"*.fits "+median_flat_name
os.system(temp)

# normalized it
median_flat=pyfits.getdata(median_flat_name)
median_flat_head=pyfits.getheader(median_flat_name)
avg = np.mean(median_flat)
median_flat = np.divide(median_flat, avg)
pyfits.writeto(median_flat_name[0:-5]+'_n.fits', median_flat, median_flat_head)
print median_flat_name+' OK'

