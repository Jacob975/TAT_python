#!/usr/bin/python
'''
Program:
This is a program the create a figure of 2D-gaussion distribution.
include paras of 
    the height of peak, 
    the size of figure, 
    the position of the peak, 
    the sigma of x_axis and y_axis, 
    and noise.
method:
1. comfirm your paras in the code with vim or vi command
2. cregau2D.py
editor Jacob975
#################################
update log
    20170402 version alpha 1
    This func can run properly

'''

import numpy as np
import time
import pyfits
from curvefit import gaussian
# measure times
start_time = time.time()
# Initialize the paras.
height = 1000
fig_width = 100 
center_x = 50
center_y = 50
sig_x = 5
sig_y = 5
noise = 3
# create gaussian distribution matrix
Xin, Yin = np.mgrid[0:fig_width+1, 0:fig_width+1]
data = gaussian(height, center_x, center_y, sig_x, sig_y)(Xin, Yin) + 3*np.random.random(Xin.shape)
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
# calculate the position of center.
pyfits.writeto('test.fits', data)
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."

