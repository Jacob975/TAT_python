#!/usr/bin/python
import numpy as np
from numpy import pi, r_
import matplotlib.pyplot as plt
from scipy import optimize
import curvefit
from sys import argv
import time
import pyfits

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

# measure times
start_time = time.time()
# get all names of fits
list_name=argv[-1]
fits_list=readfile(list_name)
del fits_list[-1]

for name in fits_list:
    data = pyfits.getdata(name)
    plt.matshow(data, cmap=plt.cm.gist_earth_r)

    params = curvefit.fitgaussian(data)
    fit = curvefit.gaussian_2D(*params)

    plt.contour(fit(*np.indices(data.shape)), cmap=plt.cm.copper)
    ax = plt.gca()
    (height, x, y, width_x, width_y) = params
    print params
'''
    plt.text(0.95, 0.05, """
x : %.1f
y : %.1f
width_x : %.1f
width_y : %.1f""" %(x, y, width_x, width_y),
        fontsize=16, horizontalalignment='right',
        verticalalignment='bottom', transform=ax.transAxes)

    plt.show()
'''
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Thread, spending ", elapsed_time, "seconds."
