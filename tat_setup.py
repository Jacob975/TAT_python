#!/usr/bin/python
'''
Program:
This is a program to setup tat python code. 
For Linux only
Usage:
1. tat_setup_linux.py
editor Jacob975
20170809
#################################
update log

20170809 version alpha 1
	It can run properly
'''
import time
import glob
import os
import fnmatch
from sys import platform, exit

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
    if VERBOSE>2:print "length of answer = {0}".format(len(answer))
    if len(answer) == 0:
        if VERBOSE>0:print "no match answer"
        return
    if len(answer) == 1:
        return answer[0]
    else:
	return answer

# This method is used to set the path in the first line of programm
def set_path_linux(py_path, path = ""):
    py_list = glob.glob("{0}/*.py".format(path))
    for name in py_list:
        temp = 'sed -i "1s?.*?{0}?" {1}'.format(py_path, name)
        if VERBOSE>0:print temp
        os.system(temp)

# This method is used to set the path in the first line of each tat_python programm file
def set_path_mac(py_path, path = ""):
    py_list = glob.glob("{0}/*.py".format(path))
    for name in py_list:
        temp = 'sed -i '' -e "1s?.*?{0}?" {1}'.format(py_path, name)
        if VERBOSE>0:print temp
        os.system(temp)
    # remove by-product
    temp = "rm *-e"
    os.system(temp)

#--------------------------------------------
# main code
VERBOSE = 1
# measure times
start_time = time.time()
py_path = get_path("path_of_python")
py_path = "#!{0}".format(py_path)
if VERBOSE>0:print "path of python or python2 writen in tat_config: {0}".format(py_path)
# get path of code from tat_config
code_path = get_path("path_of_code")
# set path of python into all tat_python program file
if platform == "linux" or platform == "linux2":
    set_path_linux(py_path, code_path)
    # process all code in nest folder
    obj_list = glob.glob("*")
    for obj in obj_list:
        if os.path.isdir(obj):
            os.chdir(obj)
            temp_path = "{0}/{1}".format(code_path, obj)
            set_path_linux(py_path, temp_path)

elif platform == "darwin":
    set_path_mac(py_path, code_path)
    # process all code in nest folder
    obj_list = glob.glob("*")
    for obj in obj_list:
        if os.path.isdir(obj):
            os.chdir(obj)
            temp_path = "{0}/{1}".format(code_path, obj)
            set_path_mac(py_path, temp_path)

else:
    print "you system is not fit the requirement of tat_python"
    print "Please use Linux of macOS"
    exit()

# back to path of code
print code_path
os.chdir(code_path)
# get path of result and source
path_of_source = get_path("path_of_source")
path_of_source = path_of_source
path_of_result = get_path("path_of_result")
path_of_result = path_of_result
# construct necessary folder
if VERBOSE>0:print "construct necessary folders..."
# source folder
temp = "mkdir -p {0}/TF/image".format(path_of_source)
os.system(temp)
temp = "mkdir -p {0}/TF/calibrate".format(path_of_source)
os.system(temp)
temp = "mkdir -p {0}/KU/image".format(path_of_source)
os.system(temp)
temp = "mkdir -p {0}/KU/calibrate".format(path_of_source)
os.system(temp)
# result folder
temp = "mkdir -p {0}/TAT_done".format(path_of_result)
os.system(temp)
temp = "mkdir -p {0}/TAT_raw_star_catalog/done".format(path_of_result)
os.system(temp)
temp = "mkdir -p {0}/limitation_magnitude_and_noise".format(path_of_result)
os.system(temp)
temp = "mkdir -p {0}/ref_catalog".format(path_of_result)
os.system(temp)
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Setup Program, spending ", elapsed_time, "seconds."
