#!/usr/bin/python
'''
Program:
This is a program to compile all python source code under current folder.
method: 
1. $py_com.py
editor Jacob975
20170318 version alpha 1
#################################
update log
'''
import os
import py_compile

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

# create a list content all names of python source code.
temp="ls *.py > list_python"
os.system(temp)
py_list=readfile("list_python")
del py_list[-1]
# remove previous mechine code
temp="rm -r *.pyc"
os.system(temp)
# compile all python source codes
for name in py_list:
    py_compile.compile(name)
# change accessibility to 744
temp="chmod 744 *.pyc"
os.system(temp)
# remove list_python
os.remove("list_python")
