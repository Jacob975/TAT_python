#!/usr/bin/python
'''
Program:
This is a program to test the psf fitting in photutils. 
Usage:
1. psf_test_iraf.py [image name]
editor Jacob975
20170809
#################################
update log

20170810 version alpha 1
    The code can run properly.
'''
#--------------------------------------------
# modules for images and tables I/O
import numpy as np
import pyfits
import time
from sys import argv
from curvefit import hist_gaussian_fitting, get_peak_filter, get_star
from tabulate import tabulate
#-------------------------------------------
# modules below are used to creating artificial image
from photutils.datasets import make_random_gaussians
from photutils.datasets import make_noise_image
from photutils.datasets import make_gaussian_sources

#--------------------------------------------------
# modules below are used to Initialize instances for the IterativelySubtractedPSFPhotometry object

from photutils.detection import DAOStarFinder, IRAFStarFinder	# source detection
from photutils.psf import DAOGroup			# grouping functionality
from photutils.psf import IntegratedGaussianPRF		# PSF model
from photutils.background import MMMBackground		# bkg estimater
from photutils.background import MADStdBackgroundRMS	# noise estimater
from astropy.modeling.fitting import LevMarLSQFitter	# fitter
from astropy.stats import gaussian_sigma_to_fwhm	# abbreviation of "gaussian sigma to fall width half maximum"

#--------------------------------------------
# module below is used to Perform photometry
from photutils.psf import IterativelySubtractedPSFPhotometry

#--------------------------------------------
# modules below is used to Plot original and residual images
from matplotlib import rcParams
import matplotlib.pyplot as plt

#--------------------------------------------
# main code
VERBOSE = 2
# measure times
start_time = time.time()
# do what you want.
#---------------------------------------------
# find out property of star in this image 
image = pyfits.getdata(argv[-1])
# test how many peak in this image.
sz = 30
tl = 5

peak_list = get_peak_filter(image, tall_limit = tl, size = sz)
# test how many stars in this figure.
hwl = 4
ecc = 1

star_list = get_star(image, peak_list, margin = 4, half_width_lmt = hwl, eccentricity = ecc)
sigma_sum = 0
for star in star_list:
	sigma_sum += star[3]
	sigma_sum += star[4]

sigma_psf = np.divide(sigma_sum, len(star_list)*2)
sigma_psf = round(sigma_psf, 2)
print "sigma_psf = {0}".format(sigma_psf)
#---------------------------------------------
# Initialize instances for the IterativelySubtractedPSFPhotometry object

bkgrms = MADStdBackgroundRMS()
std = bkgrms(image)

paras_hist, cov_hist = hist_gaussian_fitting('default', image)
bkg = paras_hist[0]
std = paras_hist[1]
# set nan on all pixel which near border within 20 pixel.
image[:,:20] = np.nan
image[:,-21:] = np.nan
image[:20,:] = np.nan
image[-21:,:] = np.nan
# wipe out all nan
nan_index = np.isnan(image)
image[nan_index] = bkg
print "bkg = {0}".format(bkg)
iraffind = IRAFStarFinder(threshold=3.0*std,
                          fwhm=sigma_psf*gaussian_sigma_to_fwhm,
                          minsep_fwhm=0.01, roundhi=5.0, roundlo=-5.0,
                          sharplo=0.0, sharphi=2.0)

daogroup = DAOGroup(2.0*sigma_psf*gaussian_sigma_to_fwhm)
mmm_bkg = MMMBackground()
psf_model = IntegratedGaussianPRF(sigma=sigma_psf)
# save model
if VERBOSE>1:
    print psf_model
    print type(psf_model)
fitter = LevMarLSQFitter()

#-------------------------------------------
# Perform photometry
print "start to photometry"
photometry = IterativelySubtractedPSFPhotometry(finder=iraffind, group_maker=daogroup,
                                                bkg_estimator=mmm_bkg, psf_model=psf_model,
                                                fitter=LevMarLSQFitter(),
                                                niters=2, fitshape=(31,31))
result_tab = photometry(image)
print "end of photometry"
residual_image = photometry.get_residual_image()

result_tab.sort('id')
if VERBOSE>1:print result_tab
# save table
result_tab.write("{0}_iraffind_tab".format(argv[-1][0:-5]), format = 'latex')

#--------------------------------------------
# Use get_star in curvefit.py to measure the count and position.
'''
# save as fits in current folder
imh = pyfits.getheader(argv[-1])
pyfits.writeto("{0}_iraffind_rest.fits".format(argv[-1][0:-5]), residual_image, imh)
sub_image = image - residual_image
pyfits.writeto("{0}_iraffind_sub.fits".format(argv[-1][0:-5]), sub_image, imh)
'''
#---------------------------------------------
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
