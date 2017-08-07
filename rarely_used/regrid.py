#!/usr/bin/python
'''
Program:
This is a program to regrid fits
We need data and transfer matrix.
method:
1. regrid.py [list name]
editor Jacob975
20170423 version alpha 1
#################################
update log

20170423 version alpha 1
    This code is under programming...
'''

from sys import argv
from math import pow
import numpy as np
import pyfits
import time

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

def regrid_argu(x, y, data, rotation_matrix_inverse):
    pre_coor = (float(x),float(y), 1.0)
    new_coor = np.dot(rotation_matrix_inverse, pre_coor)
    try:
        part_a = data[int(new_coor[0]), int(new_coor[1])] * (1-new_coor[0]%1) * (1-new_coor[1]%1)
    except IndexError:
        part_a = 0.0
    try:
        part_b = data[int(new_coor[0])+1, int(new_coor[1])] * (new_coor[0]%1) * (1-new_coor[1]%1)
    except IndexError:
        part_b = 0.0
    try:
        part_c = data[int(new_coor[0])+1, int(new_coor[1])+1] * (new_coor[0]%1) * (new_coor[1]%1)
    except IndexError:
        part_c = 0.0
    try:
        part_d = data[int(new_coor[0]), int(new_coor[1])+1] * (1-new_coor[0]%1) * (new_coor[1]%1)
    except IndexError:
        part_d = 0.0
    ans = part_a + part_b + part_c + part_d
    return ans

def regrid_data(data, rotation_matrix_inverse ):
    regrided_data = np.empty(data.shape)
    x_ref = y_ref = np.arange(data.shape[0])
    for x in x_ref:
        for y in y_ref:
            regrided_data[x, y] = regrid_argu(x, y, data, rotation_matrix_inverse )
    return regrided_data

# measure times
start_time = time.time()
'''
# get all names of fits
list_name=argv[-1]
fits_list=readfile(list_name)
del fits_list[-1]
'''
# main code
#------------------------------------

example = np.array([[0,0,0],[0,1,0],[0,0,0]], dtype =float)
rotation_matrix_inverse = np.array([[1,0,1],[0,1,0],[0,0,1]], dtype = float)
regrided_data = regrid_data(example, rotation_matrix_inverse)
print regrided_data

#------------------------------------

# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
