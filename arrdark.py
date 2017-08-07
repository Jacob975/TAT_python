#!/usr/bin/python
'''
Program:
This is a easier way to arrange dark with different exportion times.
method: 
1. Choose a folder you like 
2. $arrdark.py
editor Jacob975
20170202 version alpha 1
############################
update log

alpha 1:    20170202:
    It can run properly
'''
import os 
import pyfits
from numpy import *
from pylab import *

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

#create a list of darks
temp="ls dark*.fit > list"
os.system(temp)
#create a array of count
count=[]
#create a dictionary of quantity
quantity={}
#read list
darklist=readfile("list")
#count exptime
for name in darklist:
    succeed=False
    darkh=pyfits.getheader(name)
    time=int(darkh['EXPTIME'])
    for reftime in count:
        if reftime == time:
            quantity[str(time)]=quantity[str(time)]+1
            temp="mv "+ name +" dark_"+str(time)+"s"
            os.system(temp)
            succeed=True
            break
    if succeed :
        continue
    quantity[str(time)]=1
    count.append(time)
    temp="mkdir -p dark_"+str(time)+"s"
    os.system(temp)
    temp="mv "+ name +" dark_"+str(time)+"s"
    os.system(temp)

#print quantity
print "dark: "
for keys,values in quantity.items():
    print keys+": "+str(values)
