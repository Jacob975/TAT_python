#!/usr/bin/python
'''
Program:
    This is a easier way to add "X_*_X" on all fit file.
method:
1. choose a folder you like
2. $xmvall.py
editor Jacob975
20170207 version alpha 1
#################################
update log

20170207 alpha 1 
    It can run properly.
'''
import os 

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

temp="ls *.fit > list"
os.system(temp)

imagelist=readfile("list")
del imagelist[-1]

for name in imagelist:
    temp="mv "+name+" X_"+name+"_X"
    os.system(temp)
