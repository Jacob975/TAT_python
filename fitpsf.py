#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. std_code.py [list name]
editor Jacob975
20170318
#################################
update log
    20170318 version alpha 1
        This code is made for convenient constructing new code.
    
    20170626 version alpha 2 
    1. change name method to Usage
    2. add VERBOSE
        In detail 
        VERBOSE == 0 means no print 
        VERBOSE == 1 means printing limited result
        VERBOSE == 2 means graphing a plot or printing more detailed result
        VERBOSE == 3 means printing debug imfo
    
    20170719 version alpha 3
    1.  delete usless part, finding stdev.
    2.  add a func of reading .tsv file.
'''
from sys import argv
from math import pow
import numpy as np
import pyfits
import time
from PythonPhot import pkfit

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()

    # read in the fits images containing the target sources
    image = pyfits.getdata(fits_filename)
    noiseim = pyfits.getdata(fits_noise_filename)
    maskim = pyfits.getdata(fits_mask_filename)

    # read in the fits image containing the PSF (gaussian model
    # parameters and 2-d residuals array.
    psf = pyfits.getdata(psf_filename)
    hpsf = pyfits.getheader(psf_filename)
    gauss = [hpsf['GAUSS1'],hpsf['GAUSS2'],hpsf['GAUSS3'],hpsf['GAUSS4'],hpsf['GAUSS5']]

    # x and y points for PSF fitting
    xpos,ypos = np.array([1450,1400]),np.array([1550,1600])

    # run 'aper' on x,y coords to get sky values
    mag,magerr,flux,fluxerr,sky,skyerr,badflag,outstr = aper.aper(
            image,xpos,ypos,phpadu=1,apr=5,zeropoint=25,skyrad=[40,50],badpix=[-12000,60000],exact=True)

    # load the pkfit class
    pk = pkfit.pkfit_class(image,gauss,psf,1,1,noiseim,maskim)

    # do the PSF fitting
    for x,y,s in zip(xpos,ypos,sky):
        errmag,chi,sharp,niter,scale = pk.pkfit_norecent_noise(1,x,y,s,5)
        flux = scale*10**(0.4*(25.-hpsf['PSFMAG']))
        dflux = errmag*10**(0.4*(25.-hpsf['PSFMAG']))
        print('PSF fit to coords %.2f,%.2f gives flux %s +/- %s'%(x,y,flux,dflux))

    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
