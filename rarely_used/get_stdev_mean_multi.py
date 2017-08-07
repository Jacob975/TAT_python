#!/usr/bin/python
'''
Program:
This is a program to return std dev, mean of a fits data.
method:
1. get_stdev_mean.py [list name]
editor Jacob975
20170319 version alpha 1
#################################
update log
    20170319 alpah 1
    the program can run properly.
'''
#from statistics import mean
from sys import argv
from math import pow
import numpy as np
import pyfits
from multiprocessing import Pool
import time

def Task(name):
    imA = pyfits.getdata(name)
    imB = imA.flatten()
    fits_mean = np.mean(imB)
    fits_stdev = np.std(imB)
    temp = name+"\t"+str(fits_stdev)+"\t"+str(fits_mean)+"\n"
    fo = open("stdev_mean.log", "a")
    fo.write(temp)
    fo.close()
    return

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

if __name__ == '__main__':
    # measure times
    star_time = time.time()
    # get all name of fits
    list_name=argv[-1]
    fits_list=readfile(list_name)
    del fits_list[-1]
    fo = open("stdev_mean.log", "a")
    fo.write("#\tname\t\t\tstdev\t\tmean\n")
    fo.close()
    pool = Pool()
    pool.map(Task, fits_list)
    # measuring time
    elapesd_time = time.time() - star_time
    print "Exiting Main Process, spending ",elapesd_time, "seconds."
