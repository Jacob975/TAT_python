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

def get_path(option, VERBOSE = 1):
    setting_file = readfile("tat_config")
    answer = []
    start_index = setting_file.index(option)
    #print setting_file
    for i in xrange(len(setting_file)):
        if i == 0:
            continue
        elif setting_file[start_index + i] == 'end':
            break
        answer.append(setting_file[start_index + i])
    if len(answer) == 0:
        if VERBOSE>0:print "no match answer"
	elif len(answer) == 1:
        return answer[0]
    else:
        return answer
