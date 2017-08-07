#!/usr/bin/python
'''
Program:
This is a easier way to test the completeness of CCDTEMP, EXPTIME.
It also check if CCDTEMP < -29.5 deg.
method:
0. You need alias /home/Jacob975/bin/tat_python/chkarrcal.py
1. Choose a folder you like 
2. $chkarrcal.py
editor Jacob975
20170207 version alpha 1
#################################
update log

20170207 alpha 1 
    It can run properly.
'''
import os
import pyfits
import fnmatch
from numpy import *
from pylab import *

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

def rm_useless_alphabet():
    obj_list=os.listdir(".")
    for name in obj_list:
        for i in range(26):
            if i==23:
                continue
            if fnmatch.fnmatch(name, chr(65+i)+"*"):
                if fnmatch.fnmatch(name, '*dark*'):
                    temp="mv "+name+" "+name[1:]
                    os.system(temp)
                    break

#remove useless alphabet
rm_useless_alphabet()

#create a list of images
os.system("ls *.fit > list")
darklist= readfile("list")

#create a list of parameters
paras=['CCDTEMP','EXPTIME']

#check images
for name in darklist:
    darkh=pyfits.getheader(name)
    for para in paras:
        try :
            temp_a=darkh[para]
        except KeyError:
            temp="mv "+name+" X_"+name+"_X"
            os.system(temp)
            break
    img_temp=darkh['CCDTEMP']
    if img_temp >= -29.5:
        temp="mv "+name+" X_"+name+"_X"
        os.system(temp)

temp="arrdark.py"
os.system(temp)
temp="arrflat.py"
os.system(temp)

