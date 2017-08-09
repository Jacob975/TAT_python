#!/usr/bin/python
'''
Program:
This is a program to demo the psf fitting.
all code is copy from https://github.com/astropy/photutils-datasets/blob/master/notebooks/ArtificialCrowdedFieldPSFPhotometry.ipynb
Usage:
1. psf_example_2.py
editor Jacob975
20170809
#################################
update log

20170809 version alpha 1
	The code can run properly.
'''
import numpy as np
import pyfits
import time
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
# modules for Photometry with fixed positions
from photutils.psf import BasicPSFPhotometry

#--------------------------------------------
# main code
VERBOSE = 1
# measure times
start_time = time.time()
# do what you want.
num_sources = 150
min_flux = 500
max_flux = 5000
min_xmean = 16
max_xmean = 240
sigma_psf = 2.0

starlist = make_random_gaussians(num_sources, [min_flux, max_flux],
                                 [min_xmean, max_xmean],
                                 [min_xmean, max_xmean],
                                 [sigma_psf, sigma_psf],
                                 [sigma_psf, sigma_psf],
                                 random_state=123)

shape = (256, 256)
image = (make_gaussian_sources(shape, starlist) +
         make_noise_image(shape, type='poisson', mean=6., random_state=123) + 
         make_noise_image(shape, type='gaussian', mean=0., stddev=2., random_state=123))
if VERBOSE>1:print starlist

#---------------------------------------------
# Initialize instances for the IterativelySubtractedPSFPhotometry object
bkgrms = MADStdBackgroundRMS()
std = bkgrms(image)

iraffind = IRAFStarFinder(threshold=3.5*std,
                          fwhm=sigma_psf*gaussian_sigma_to_fwhm,
                          minsep_fwhm=0.01, roundhi=5.0, roundlo=-5.0,
                          sharplo=0.0, sharphi=2.0)

daogroup = DAOGroup(2.0*sigma_psf*gaussian_sigma_to_fwhm)
mmm_bkg = MMMBackground()
psf_model = IntegratedGaussianPRF(sigma=sigma_psf)
fitter = LevMarLSQFitter()

#-------------------------------------------
# Perform photometry
photometry = IterativelySubtractedPSFPhotometry(finder=iraffind, group_maker=daogroup,
                                                bkg_estimator=mmm_bkg, psf_model=psf_model,
                                                fitter=LevMarLSQFitter(),
                                                niters=2, fitshape=(11,11))
result_tab = photometry(image)
residual_image = photometry.get_residual_image()

#-------------------------------------------
# Plot original and residual images

rcParams['image.cmap'] = 'viridis'
rcParams['image.aspect'] = 1  # to get images with square pixels
rcParams['figure.figsize'] = (20,10)
rcParams['image.interpolation'] = 'nearest'
rcParams['image.origin'] = 'lower'
rcParams['font.size'] = 14

simulated_result = plt.figure("Simulated data")
plt.imshow(image)
plt.title('Simulated data')
plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
if VERBOSE>0:simulated_result.show()

residual_result = plt.figure("Residual")
plt.imshow(residual_image)
plt.title('Residual')
plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
if VERBOSE>0:
	residual_result.show()

result_tab.sort('id')
if VERBOSE>1:print result_tab

#--------------------------------------------
# Photometry with fixed positions

psf_model.x_0.fixed = True
psf_model.y_0.fixed = True

positions = starlist['x_mean', 'y_mean']
positions['x_mean'].name = 'x_0'
positions['y_mean'].name = 'y_0'

photometry = BasicPSFPhotometry(group_maker=daogroup, bkg_estimator=mmm_bkg,
                                psf_model=psf_model, fitter=LevMarLSQFitter(),
                                fitshape=(11,11))
result_tab = photometry(image=image, positions=positions)
residual_image = photometry.get_residual_image()

#--------------------------------------------
# plot section

residual_fix_result = plt.figure("Residual_fix")
plt.imshow(residual_image)
plt.title('Residual_fixed')
plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
if VERBOSE>0:
	residual_fix_result.show()
	raw_input()

#---------------------------------------------
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
