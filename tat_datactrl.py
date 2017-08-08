#!/usr/bin/python
'''
Program:
This is a program to control how to read and process tat data. 
Usage:
    0. Put this code with target code in the same direction.
    1. import tat_datactrl.py in the target code.
    2. enjoy this code.
editor Jacob975
20170808
#################################
update log

20170808 version alpha 1
    
'''

import numpy as np
import pyfits

#---------------------------------------------------------
# Function in this section is for reading txt like data.

# This is used to read a list of fits name.
def readfile(filename):
    f = open(filename, 'r')
    data = []
    for line in f.readlines():
        # skip if no data or it's a hint.
        if line == "\n" or line.startswith('#'):
            continue
        data.append(line[:-1])
    f.close
    return data

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


#---------------------------------------------------------
# Function in this section is for read path from setting.
def get_path(option, VERBOSE = 0):
    setting_file = readfile("/home/Jacob975/bin/tat_python/tat_config")
    if VERBOSE>0:
        for sentence in setting_file:
            print sentence
    if option == "source":
        answer = setting_file[0]
        return answer
    elif option == "code":
        answer = setting_file[1]
        return answer
    elif option == "result":
        answer = setting_file[2]
        return answer
    else:
        print "illegal command"
        return 0
