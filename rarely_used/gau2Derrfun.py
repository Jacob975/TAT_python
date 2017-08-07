#!/usr/bin/python
'''
Program:
This is a program to fitting 2D gaussian curve.
This program only can use on one image at once.
method:
1. gau2Derrfun.py [image name]
editor Jacob975
#################################
update log
    20170417 version alpha 1 
    the program is under self testing.
'''
import numpy as np
from numpy import pi, r_
import matplotlib.pyplot as plt
from scipy import optimize
import curvefit

# Create the gaussian data
Xin, Yin = np.mgrid[0:201, 0:201]
data = curvefit.gaussian_2D(3, 100, 100, 20, 20)(Xin, Yin) + np.random.random(Xin.shape)

plt.matshow(data, cmap=plt.cm.gist_earth_r)

params = curvefit.fitgaussian(data)
fit = curvefit.gaussian_2D(*params)

plt.contour(fit(*np.indices(data.shape)), cmap=plt.cm.copper)
ax = plt.gca()
(height, x, y, width_x, width_y) = params

plt.text(0.95, 0.05, """
x : %.1f
y : %.1f
width_x : %.1f
width_y : %.1f""" %(x, y, width_x, width_y),
        fontsize=16, horizontalalignment='right',
        verticalalignment='bottom', transform=ax.transAxes)

plt.show()
