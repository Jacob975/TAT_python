#!/usr/bin/python
'''
Program:
This is a program, get result of images divied by flat.
method: 
1. Choose a folder, which contain images had been subtracted by dark, flat been subtracted by dark.
2. $division_list.py [image list] [flat]
editor Jacob975
20170219 version alpha 1
#################################
update log

20170219 alpha 1
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
flat_name=argv[-1]
imagelistname=argv[-2]
imagelist=readfile(imagelistname)
# division
flat_n=pyfits.getdata(flat_name)
for name in imagelist:
    imA=pyfits.getdata(name)
    imAh=pyfits.getheader(name) 
    imB = np.divide(imA, flat_n)
    pyfits.writeto(name[0:-5]+'_divFLAT.fits',imB,imAh)
    print name[0:-5]+'_divFLAT.fits OK '
