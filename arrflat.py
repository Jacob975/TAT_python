#!/usr/bin/python
'''
Program:
This is a easier way to arrange flats with different filter and exptime.
method: 
1. Choose a folder you like 
2. $arrflat.py
editor Jacob975
20170218 version alpha 1
#################################
update log

20170218 alpha 1
    It can run properly
'''
import os 
import pyfits
import fnmatch
from sys import exit

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer == "":
        del answer[-1]
    return answer

#create a list of flats
os.system("ls *flat*.fit > list")
flatlist=readfile("list")
if len(flatlist) == 0:
    exit("NO flat")
#create a list to count the number of filter and exptime
sample_count=[[0 for z in range(2)]for x in range(26)]
#identify number of the exptime and filter of each flats
for name in flatlist:
    if name == "":
        continue
    flath=pyfits.getheader(name)
    for j in range(26):  
        if fnmatch.fnmatch(name,chr(65+j)+"*"):
            sample_count[j][0]=sample_count[j][0]+1
            time=int(flath['EXPTIME'])
            sample_count[j][1]=time

#print count
print "flat:"
for i in range(len(sample_count)):
    if sample_count[i][0] != 0:
        print chr(65+i)+"_"+str(sample_count[i][1])+"s: "+str(sample_count[i][0])

#create folders
for i in range(len(sample_count)):
    if sample_count[i][0]!=0:
        temp="mkdir -p flat_"+chr(65+i)+"_"+str(sample_count[i][1])+"s"
        os.system(temp)

#move
for name in flatlist:
    for i in range(26):
        alphabet=chr(65+i)
        if fnmatch.fnmatch(name,alphabet+"*"):
            temp="mv "+name+" flat_"+alphabet+"_"+str(sample_count[i][1])+"s"
            os.system(temp)
            break
