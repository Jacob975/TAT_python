#!/usr/bin/python
'''
Program:
This is a program to read formated data in hard disk
and graph data in X-windows.
Usage:
powergrapher.py [stack option] [scale option] [fittiong option] [list name]
stack option :
    0. default : 
        single
    1. single :
        all data graph in one window.
    2. multi :
        each data graph in diff windows.
    3. TBA...

scale option :
    0. default : 
        linear
    1. linear :
        the scale of axes are linear
    2. log_X : 
        the scale of axes are log_X
    3. log : 
        the scale of axes are natural log
    4. pow_X : 
        the scale of axes are power by X
    5. pow : 
        the scale of axes are power by exponiantial

fitting option :
    0. default : 
        no fitting
    1. linear : 
        do linear fitting
        fitting func : y = Ax +B
    2. gaussian :
        TBA
    3. TBA :
editor Jacob975
20170629 version alpha 1
#################################
update log
    20170629 version alpha 1 
    1. Define name of parameters of Usage
    2. Define VERBOSE
        In detail 
        VERBOSE == 0 means no print 
        VERBOSE == 1 means printing limited result
        VERBOSE == 2 means graphing a plot or printing more detailed result
        VERBOSE == 3 means printing debug info

    20170702 version alpha 2

'''
from sys import argv
import numpy as np
import time

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while (answer[-1] == ""):
        del answer[-1]
    return answer

def grapher(data_name):
    line = readfile(data_name)
#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()
# read arguments
list_name = argv[-1]
stack_option = argv[1]
scale_option = argv[2]
fitting_option = argv[3]
# get all names of data
list_name = argv[-1]
data_list = readfile(list_name)
# graph figures according to options.
print stack_option
print scale_option
print fitting_option
for name in data_list:
    print "Current file: ", name
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
