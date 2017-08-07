#!/usr/bin/python
'''
Program:
This is a program to fit gaussian distribution, get mean, stdev, cov and cor of fits in selected list.
method:
1. histgaufit.py [selected list]
editor Jacob975
#################################
update log

    20170321 alpha 1
    It can run porperly.

    20170328 alpha 2
    Changeing the name of the program from gaussingfitting.py to histgaufit.py
'''
from sys import argv
from curvefit import hist_gaussian_fitting
from multiprocessing import Pool
import matplotlib.pyplot as plt
import pyfits
import numpy as np
import time

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

def Task(name):
    imA = pyfits.getdata(name)
    imB = imA.flatten()
    parameters, cov, cor = hist_gaussian_fitting(imB, delta = 15, shift = -7)
    print name, "\tmu: ", parameters[0],"stdev: ", parameters[1] ,"cov: ",cov, "cor: ", cor
    fo = open("gaussian_fitting.log", "a")
    fo.write('%s\t%f\t%f\t%f\t%f\n'%(name, parameters[0], parameters[1], cov, cor))
    fo.close()
    return 

if __name__ == '__main__':
    # measure times
    start_time = time.time()
    # read files
    list_name = argv[-1]
    fits_list = readfile(list_name)
    del fits_list[-1]
    # write title
    fo = open("gaussian_fitting.log","a")
    fo.write('#\tname\t\t\tmu\t\tstdev\t\tcovariance\tcorelation\n')
    fo.close()
    pool = Pool()
    pool.map(Task, fits_list)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
