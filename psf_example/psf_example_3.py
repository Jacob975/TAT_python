#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. std_code.py [list name]
editor Jacob975
20170815
#################################
update log

'''
#-------------------------------------------
# 
import time
import numpy as np

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.io import fits
from astropy.modeling import models, fitting

import photutils
from photutils import psf

from matplotlib import rcParams
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
rcParams['image.cmap'] = 'viridis'
rcParams['image.aspect'] = 1  # to get images with square pixels
rcParams['figure.figsize'] = (15,10)
rcParams['image.interpolation'] = 'none'

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()   
    #----------------------------------------------
    gmod = models.Gaussian2D(x_stddev=5, y_stddev=5)
    # without arguments, `render` creates an image based on the bounding_box, which defaults to 5.5 sigma
    figure = plt.figure("exampe_1")
    plt.imshow(gmod.render(), vmin=0, vmax=1)
    plt.colorbar()
    figure.show()
    #------------------------------------------------
    gmod.bounding_box
    # this is a subtly different Gaussian that is integrated over pixels
    gmodi = psf.IntegratedGaussianPRF(sigma=5)
    # make it match the above plot
    gmodi.bounding_box = gmod.bounding_box
    figure = plt.figure("example_2")
    plt.imshow(gmodi.render())
    plt.colorbar()
    figure.show()
    #-------------------------------------------------
    # also compare the IntegratedGaussianPRF to the Gaussian2DModel.  Note that we need to re-scale the flux to match the Gaussian2D
    figure = plt.figure("example_3")
    plt.imshow(gmod.render() - gmodi.render()/gmodi.render().max())
    plt.colorbar()
    figure.show()
    raw_input()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
