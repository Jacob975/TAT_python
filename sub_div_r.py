#!/usr/bin/python
'''
Program:
This is a collected method of subtracting by dark, dividing by flat, rotating. 
method:	    
1.  Choose a folder contain some fits you want to process.
2.  $sub_div_r.py   # The code will do sub, div, rot automatically.
editor:	    Jacob975
20170124
#############################
update log

20170124 alpha 1
    The program can run properly

20170216 alpha 2
    advance the efficient of program, change some name of variable as offen used.

20170219 alpha 3 
    add a new function let image divided by flat.

20170301 alpha 4
    Pause funcs of rotate_3sigma series.
    not finished yet

20170711 alpha 5 
    include rotate image func.

20170719 alpha 6 
    add new header file for this code.
    rotate, subtract dark and divide flat is moved to fit_lib.py

#############################
'''
import os
import fnmatch
import pyfits
import numpy as np
import fit_lib
from tat_datactrl import readfile
from sys import exit


#--------------------------------------
# main code 
VERBOSE = 0
temp="ls *fit > list"
os.system(temp)

imagelist=os.listdir(".")
dark_success = 0
flat_success = 0
# subtracted by dark
for name in imagelist:
    if fnmatch.fnmatch(name,"Median_dark*"):
        dark_success = 1
        fit_lib.subtract_list("list", name)
        break

temp="ls *subDARK.fits > list_subDARK"
os.system(temp)
# divided by flat
for name in imagelist:
    if fnmatch.fnmatch(name, "Median_flat*"):
        flat_success = 1
        fit_lib.division_list("list_subDARK", name)
        break

temp="ls *divFLAT.fits > list_divFLAT"
os.system(temp)
# path related argument
path=os.getcwd()
list_path=path.split("/")
telescope=list_path[-5]
date=list_path[-3]
obj=list_path[-2]
filter_exp=list_path[-1]
temp_list=filter_exp.split("_")
header=temp_list[0]
# read subDARK list or divFLAT list
# and rotate images with subDARK or divFLAT
if dark_success == 1 and flat_success != 1:
    list_subDARK = readfile("list_subDARK")
    fit_lib.rotate(telescope, list_subDARK)
    '''
    temp = "rm *subDARK.fits"
    '''
    os.system(temp)
if dark_success == 1 and flat_success == 1:
    list_divFLAT = readfile("list_divFLAT")
    fit_lib.rotate(telescope, list_divFLAT)
    temp = "rm *subDARK.fits"
    os.system(temp)
    temp = "rm *divFLAT.fits"
    os.system(temp)
    temp = "ls *_r.fits > list_divFLAT"
    os.system(temp)
