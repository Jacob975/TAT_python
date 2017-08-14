#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. create_an_artificial_image.py [list name]
editor Jacob975
20170809
#################################
update log

20170810 version alpha 1
    The code can run properly.
'''
import numpy as np
import pyfits
import time
from sys import argv
from curvefit import hist_gaussian_fitting, get_peak_filter, get_star
from tabulate import tabulate
##-------------------------------------------
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
#---------------------------------------------
# find out property of star in this image 
image = pyfits.getdata(argv[-1])
# test how many peak in this image.
# If too much, raise up the limitation of size
sz = 30
tl = 5
'''
peak_list = []
while len(peak_list) >500 or len(peak_list) < 3:
    sz +=1
    peak_list = get_peak_filter(image, tall_limit = tl, size = sz)
if VERBOSE>2:
    print "peak list: "
    for peak in peak_list:
        print peak[1], peak[0]
'''
peak_list = get_peak_filter(image, tall_limit = tl, size = sz)
# test how many stars in this figure.
# If too much, raise up the limitation of half_width with default = 4
hwl = 4
ecc = 1
'''
star_list = []
while len(star_list) > 20 or len(star_list) < 3:
    hwl += 1
    star_list = get_star(image, peak_list, margin = 4, half_width_lmt = hwl, eccentricity = ecc)
    if VERBOSE>0:print "hwl = {0}, len of ref_star_list = {1}".format(hwl, len(star_list))
'''
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
'''
daofind = DAOStarFinder(fwhm = sigma_psf*gaussian_sigma_to_fwhm,
                        threshold = 5. * std)
'''
daogroup = DAOGroup(2.0*sigma_psf*gaussian_sigma_to_fwhm)
mmm_bkg = MMMBackground()
psf_model = IntegratedGaussianPRF(sigma=sigma_psf)
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

#-------------------------------------------
# Plot original and residual images

if VERBOSE>1:
    rcParams['image.cmap'] = 'viridis'
    rcParams['image.aspect'] = 1  # to get images with square pixels
    rcParams['figure.figsize'] = (20,10)
    rcParams['image.interpolation'] = 'nearest'
    rcParams['image.origin'] = 'lower'
    rcParams['font.size'] = 14
    # display origin image
    simulated_result = plt.figure("Simulated data")
    plt.imshow(image)
    plt.title('Simulated data')
    plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
    simulated_result.show()
    # display residual part
    residual_result = plt.figure("Residual")
    plt.imshow(residual_image)
    plt.title('Residual')
    plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
    residual_result.show()

result_tab.sort('id')
if VERBOSE>1:print result_tab

# save table
result_file = open("{0}_iraffind_tab".format(argv[-1][0:-5]), "w")
result_file.write(tabulate(result_tab))
result_file.close()

# save as fits in current folder
imh = pyfits.getheader(argv[-1])
pyfits.writeto("{0}_iraffind_rest.fits".format(argv[-1][0:-5]), residual_image, imh)
sub_image = image - residual_image
pyfits.writeto("{0}_iraffind_sub.fits".format(argv[-1][0:-5]), sub_image, imh)
'''
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
'''
#---------------------------------------------
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
