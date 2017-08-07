#!/usr/bin/python
'''
Program:
This is a program of generate the limitation magnitude from database.
Usage:
1. lim_mag.py [date] [scope] [band] [method] [exptime]

date:
    The date taking photos.
    It should be a 8-digits number.
    e.g. 20170724
    If you type in "a", you will get limitation magnitude on all date.

scope:
    The scope be used.
    It should be a "KU" or "TF".
    e.g. KU
    If you type in "a", you will get limitation magnitude on all scope.

band:
    The band we used.
    It should be a english letter.
    e.g. N
    If you type in "a", you will get all limitation magnitude on all band.

method:
    The method used to stack images.
    It should be "mdn" or "mean"
    e.g. mdn
    If you type in "a", you will get all limitation magnitude of all method.

obj:
    The main object in this image.
    It should be one of words in obj_list below.
    e.g. SgrNova
    If you type in "a", you will get all object.

exptime:
    The exptime of photo.
    It should be a number in sec.
    default : 600
    e.g. 600

Usage : 
    $lim_mag.py 600                             # exptime should be the lastest argument.
    $lim_mag.py 20170518 600                    # date will be set as 20170518.
    $lim_mag.py KU 600                          # scope will be set as KU.
    $lim_mag.py N 600                           # band will be set as N_40s.
    $lim_mag.py mdn 600                         # stack method will be set as mdn.
    $lim_mag.py 600                             # exptime will be set as 600s.
    $lim_mag.py SgrNova 600                     # object will be set as SgrNova.
    $lim_mag.py 20170518 KU 600                 # you can use two arguments. 
    $lim_mag.py KU 20170518 600                 # order of arguments is trivial.
    $lim_mag.py 20170518 TF N mdn 600           # you can use at most 5 arguments.

editor Jacob975
20170724
#################################
update log

20170724 version alpha 1
    It works properly.

20170801 version alpha 2
    1.  add new argument "object".
    2.  renew previous argument "band".
        details please read header file.
'''
from sys import argv
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

def get_order(tar_list, property_name_list):
    # determine the order of all property.
    ord_list = [ 0 for i in range(len(property_name_list))]
    for i in xrange(len(tar_list[0])):
        for j in xrange(len(property_name_list)):
            if tar_list[0][i] == property_name_list[j]:
                ord_list[j] = i
                break
    return ord_list

def select_property(tar_list, property_list, ord_list, property_name_list, VERBOSE = 0):
    # create a empty list with length of property list
    temp_list = [ [] for i in range(len(property_list)) ] 
    # append original list to back
    # It wiil seem as
    # temp_list = [   [], [], [], ... ,[tar_list]  ]
    temp_list.append(tar_list)
    for i in xrange(len(ord_list)):
        if VERBOSE>0:print "current property = ",property_list[i]
        if property_list[i] == "a":
            temp_list[i] = temp_list[i-1]
        if property_name_list[i] == "band": 
            for tar in temp_list[i-1]: 
                if tar[ord_list[i]][0] == property_list[i]:
                    temp_list[i].append(tar)
            continue
        else:
            for tar in temp_list[i-1]:
                if tar[ord_list[i]] == property_list[i]:
                    temp_list[i].append(tar)
    return temp_list[len(property_list)-1]

# Determine this two data are the same at these orders.
def match_data(noise, ord_list_noise, del_m, ord_list_del_m):
    for i in xrange(len(ord_list_noise)):
        if noise[ord_list_noise[i]] != del_m[ord_list_del_m[i]]:
            return False
    return True
#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()
# get property from argv
if len(argv) == 1:
    print "Usage: lim_mag.py [date] [scope] [band] [method] [obj] [exptime]"
    exit(0)

date = "a"
scope = "a"
band = "a"
letter_list = ["A", "B", "C", "V", "R", "N"]
method = "a"
obj = "a"
obj_list = ["NGC1333", "KELT-17", "Groombridge1830", "WD1253+261", "SgrNova", "HH32", "KIC8462852", "PN", "61Cygni", "IC5146"]
exptime = 600

if len(argv) == 2:
    exptime = float(argv[-1])
else:
    for i in xrange(len(argv)):
        if i == len(argv) -1:
            continue
        # Is it a date?
        try:
            float(argv[i])
        except :
            pass
        else:
            date = argv[i]
        # Is it a scope?
        if argv[i] =="KU" or argv[i] == "TF":
            scope = argv[i]
        # Is it a band?
        elif len(argv[i]) == 1:
            for letter in letter_list:
                if argv[i] == letter:
                    band = letter
                    continue
        # Is it a method?
        elif argv[i] == "mdn" or argv[i] == "mean":
            method = argv[i]
        # Is it a object?
        else:
            for name in obj_list:
                if name == argv[i]:
                    obj = name
                    continue

    exptime = float(argv[-1])
property_list = [date, scope, band, method, obj]
property_name_list = ["date", "scope", "band", "method", "object"]
# read del_m tsv
path_of_del_m = "/home/Jacob975/demo/limitation_magnitude_and_noise/delta_mag.tsv"
list_del_m = read_tsv_file(path_of_del_m)
# read noise tsv
path_of_noise = "/home/Jacob975/demo/limitation_magnitude_and_noise/noise_in_mag.tsv"
list_noise = read_tsv_file(path_of_noise)
# get order of property in .tsv file
ord_list_del_m = get_order(list_del_m, property_name_list)
ord_list_noise = get_order(list_noise, property_name_list)
# select suitable star
del list_del_m[0]
list_del_m = select_property(list_del_m, property_list, ord_list_del_m, property_name_list)
if VERBOSE>0: print list_del_m
del list_noise[0]
list_noise = select_property(list_noise, property_list, ord_list_noise, property_name_list)
if VERBOSE>0: print list_noise
# calculate limitation of magnitude
for noise in list_noise:
    for del_m in list_del_m:
        if match_data(noise, ord_list_noise, del_m, ord_list_del_m):
            print "object: {5}, date: {0}, scope: {1}, band: {2}, method: {3}, catalog_band: {4}".format(noise[ord_list_noise[0]], noise[ord_list_noise[1]], noise[ord_list_noise[2]], noise[ord_list_noise[3]], del_m[-2], noise[0])
            amp = float(noise[-4])
            const = float(noise[-2])
            delta_m = float(del_m[0])
            if VERBOSE>0:print amp, const, delta_m
            answer = amp*np.log10(exptime) - 2.5*np.log10(3) + const + delta_m
            print "limitation magnitude = {0:.2f}".format(answer)
# save
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
