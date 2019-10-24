#!/usr/bin/python3
'''
Abstract:
    This is a program for convert units 
    ukirt: mJy, Jy, mag supported
Usage:
    1. Choose a python file you like
    2. Write down "import convert_lib" some where
Editor:
    Jacob975

##################################
#   Python3                      #
#   This code is made in python3 #
##################################

20180502
####################################
update log
20180502 version alpha 1
    1. the code work
20180531 version alpha 2
    1. add a group of funcs for converting between pixel and wcs
    but they haven't been tested.
20180604 version alpha 3
    1. update the parameter of system.
'''
import numpy as np

####################################
from uncertainties import unumpy, ufloat
# How to cite this package
# If you use this package for a publication (in a journal, on the web, etc.), 
# please cite it by including as much information as possible from the following: 
# Uncertainties: a Python package for calculations with uncertainties, Eric O. LEBIGOT, 
# http://pythonhosted.org/uncertainties/. Adding the version number is optional.

#-------------------------------------------------------
# convertion with error
def Jy_to_mJy(flux_density, err_flux_density):
    return 1000.0 * flux_density, 1000.0 * err_flux_density

def mJy_to_Jy(flux_density, err_flux_density):
    return flux_density / 1000.0, err_flux_density / 1000.0

def mag_to_Jy(zeropoint, magnitude, err_magnitude):
    flux_density = zeropoint * np.power( 10.0, -0.4 * magnitude )
    upper_flux_density = zeropoint * np.power(10.0, -0.4 * (magnitude - err_magnitude))
    err_flux_density = upper_flux_density - flux_density
    return flux_density, err_flux_density

def Jy_to_mag(zeropoint, flux_density, err_flux_density):
    magnitude = -2.5 * ( np.log(flux_density) - np.log(zeropoint) )/ np.log(10.0)
    upper_magnitude = -2.5 * ( np.log(flux_density - err_flux_density) - np.log(zeropoint) )/ np.log(10.0)
    err_magnitude = upper_magnitude - magnitude
    return magnitude, err_magnitude

def mag_to_mJy(zeropoint, magnitude, err_magnitude):
    flux_density, err_flux_density = mag_to_Jy(zeropoint, magnitude, err_magnitude)
    flux_density, err_flux_density = Jy_to_mJy(flux_density, err_flux_density)
    return flux_density, err_flux_density

def mJy_to_mag(zeropoint, flux_density, err_flux_density):
    flux_density, err_flux_density = mJy_to_Jy(flux_density, err_flux_density)
    magnitude, err_magnitude = Jy_to_mag(zeropoint, flux_density, err_flux_density)
    return magnitude, err_magnitude

