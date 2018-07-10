#!/usr/bin/python
'''
Program:
This is a program to setup tat python code. 
For Linux and macOS only
Usage:
1. tat_setup.py
editor Jacob975
20170809
#################################
update log

20170809 version alpha 1
    It can run properly

20170830 version alpha 2
    1. combine the linux version and macOS version

20171114 version alpha 3:
    1. Using py to save environment constant instead of a dat file.
20180625 versiona alpha 4:
    1. Path of result is removed
'''
import time
import glob
import os
import fnmatch
import TAT_env
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
# get the path of python from TAT_env.py
py_path = TAT_env.path_of_python
py_path = "#!{0}".format(py_path)
if VERBOSE>0:print "path of python or python2 writen in tat_config: {0}".format(py_path)
# get path of TAT code from TAT_env
code_path = TAT_env.path_of_code
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
            os.chdir("..")

elif platform == "darwin":
    set_path_mac(py_path, code_path)
    # process all code in nest folder
    obj_list = glob.glob("*")
    for obj in obj_list:
        if os.path.isdir(obj):
            os.chdir(obj)
            temp_path = "{0}/{1}".format(code_path, obj)
            set_path_mac(py_path, temp_path)
            os.chdir("..")

else:
    print "you system is not fit the requirement of tat_python"
    print "Please use Linux of macOS"
    exit()

# back to path of code
print code_path
os.chdir(code_path)
# get path of source from TAT_env
path_of_image = TAT_env.path_of_image
# construct necessary folder
if VERBOSE>0:print "construct necessary folders..."
# source folder
temp = "mkdir -p {0}/TF/image".format(path_of_image)
os.system(temp)
temp = "mkdir -p {0}/TF/calibrate".format(path_of_image)
os.system(temp)
temp = "mkdir -p {0}/TF/log".format(path_of_image)
os.system(temp)
temp = "mkdir -p {0}/KU/image".format(path_of_image)
os.system(temp)
temp = "mkdir -p {0}/KU/calibrate".format(path_of_image)
os.system(temp)
temp = "mkdir -p {0}/KU/log".format(path_of_image)
os.system(temp)
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Setup Program, spending ", elapsed_time, "seconds."
