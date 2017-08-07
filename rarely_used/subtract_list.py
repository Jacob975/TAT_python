#!/usr/bin/python
'''
Program:
This is a program, get result of images subtracted by dark.
method: 
1. Choose a folder, which contain images and dark .
2. $subtract_list.py [image list] [dark]
editor Jacob975
20170719
#################################
update log

20170719 alpha 1
    It can run properly.
'''
import os
import pyfits
from sys import argv
import numpy as np

def readfile(filename):
    file= open(filename)
    answer_1= file.read()
    answer= answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

# get data
dark_name=argv[-1]
imagelistname=argv[-2]
imagelist=readfile(imagelistname)
# division
dark=pyfits.getdata(dark_name)
for name in imagelist:
    imA=pyfits.getdata(name)
    imAh=pyfits.getheader(name) 
    imB = np.subtract(imA, dark)
    pyfits.writeto(name[0:-5]+'_subDARK.fits',imB,imAh)
    print name[0:-5]+'_subDARK.fits OK '
