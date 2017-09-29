#!/usr/bin/python
'''
Program:
This is a program to test the pyphot. 
Usage:
1. psf_pyphot.py [fits_name] [star_table]

fits_name:
    The stars on this image will setup the psf model.

star_table:
    This is a table save the coor of star on the image in pixel unit.
editor Jacob975
20170906
#################################
update log

20170906 version alpha 1
'''
import time                                     # time controller
from sys import argv                            # argument I/O
from PythonPhot import getpsf                   # psf generater
from PythonPhot import aper                     #
from PythonPhot import rdpsf                    #
from PythonPhot import pkfit                    # fitting psf model
from astropy.io import fits as pyfits           # fits image I/O
from astropy.table import Table                 # fits Table I/O
from astropy.stats import gaussian_sigma_to_fwhm
from curvefit import get_peak_filter, get_star, hist_gaussian_fitting
import numpy as np

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    fits_filename=argv[-2]
    table_name = argv[-1]
    # do what you want.
    # grab data, both image and star table
    image = pyfits.getdata(fits_filename)
    star_table = Table.read(table_name)
    paras, cov = hist_gaussian_fitting("Default", image)
    mean = paras[0]
    noise = paras[1]
    try:
        xs_array = np.array(star_table['xsigma'])
        ys_array = np.array(star_table['ysigma'])
    except:
        xs_array = np.array(star_table['sigma_x'])
        ys_array = np.array(star_table['sigma_y'])
    sigma_psf = np.mean(np.array([xs_array, ys_array]))
    print sigma_psf
    # read star region
    coo_table = Table.read(table_name)
    try:
        xpos,ypos = np.array(coo_table['Ycoord']),np.array(coo_table['Xcoord'])
    except:
        xpos, ypos = np.array(coo_table['xcenter']), np.array(coo_table['ycenter'])
    # run aper to get mags and sky values for specified coords
    mag, magerr, flux, fluxerr, sky, skyerr, badflag, outstr = aper.aper(
            image, xpos, ypos, phpadu=1, apr=5, zeropoint = mean, skyrad=[40,50],badpix=[-12000,50000],exact=True)
    # use the stars at those coords to generate a PSF model
    psf_name = "{0}_psf.fits".format(fits_filename[:-5])
    fwhm = sigma_psf*gaussian_sigma_to_fwhm
    if VERBOSE>0:
        print "fwhm = {0}".format(fwhm)
    gauss, psf, psfmag = getpsf.getpsf(image, xpos, ypos, mag, sky, 0.05 , 1.0, np.arange(len(xpos)), 10, fwhm, "temp_psf.fits")
    # reread
    psf, hpsf = rdpsf.rdpsf("temp_psf.fits")
    # save result
    pyfits.writeto(psf_name, psf, header = hpsf, clobber = True)
    #------------------------------------
    # fitting section
    # load the pkfit class
    pk = pkfit.pkfit_class(image, gauss, psf, 0.05, 1)
    # do the PSF fitting
    for x,y,s in zip(xpos,ypos,sky):
        errmag, chi, sharp, niter, scale = pk.pkfit(1, x, y, s, 10, debug = False)
        flux = scale*10**(0.4*(25.-hpsf['PSFMAG']))
        dflux = errmag*10**(0.4*(25.-hpsf['PSFMAG']))
        print('PSF fit to coords %.2f,%.2f gives flux %s +/- %s'%(x,y,flux,dflux))
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
