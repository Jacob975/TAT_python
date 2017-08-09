#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. std_code.py [list name]
editor Jacob975
20170809
#################################
update log

'''
#---------------------------------------------------
# import module below is for create simulated image.
import pyfits
import time
import numpy as np
from astropy.table import Table
from photutils.datasets import make_random_gaussians, make_noise_image
from photutils.datasets import make_gaussian_sources
from matplotlib import rcParams
import matplotlib.pyplot as plt

#---------------------------------------------------
# import module below is for psf fitting.
from photutils.detection import IRAFStarFinder
from photutils.psf import IntegratedGaussianPRF, DAOGroup
from photutils.background import MMMBackground, MADStdBackgroundRMS
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.stats import gaussian_sigma_to_fwhm
from photutils.psf import IterativelySubtractedPSFPhotometry

#--------------------------------------------
# main code
VERBOSE = 0
# measure times
start_time = time.time()

# do what you want.
sigma_psf = 2.0
sources = Table()
sources['flux'] = [700, 800, 700, 800]
sources['x_mean'] = [12, 17, 12, 17]
sources['y_mean'] = [15, 15, 20, 20]
sources['x_stddev'] = sigma_psf*np.ones(4)
sources['y_stddev'] = sources['x_stddev']
sources['theta'] = [0, 0, 0, 0]
sources['id'] = [1, 2, 3, 4]
tshape = (32, 32)
image = (make_gaussian_sources(tshape, sources) + make_noise_image(tshape, type='poisson', mean=6., random_state=1) + make_noise_image(tshape, type='gaussian', mean=0., stddev=2., random_state=1))

rcParams['font.size'] = 13
simulated_png = plt.figure("simulated.png")
plt.imshow(image, cmap='viridis', aspect=1, interpolation='nearest', origin='lower')
plt.title('Simulated data') 
plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
plt.savefig("/Users/jacob975/Documents/tat_data/test/simulated.png")
simulated_png.show()

#-------------------------------------------
# Below is psf fitting section

bkgrms = MADStdBackgroundRMS()
std = bkgrms(image)
iraffind = IRAFStarFinder(threshold=3.5*std, fwhm=sigma_psf*gaussian_sigma_to_fwhm, minsep_fwhm=0.01, roundhi=5.0, roundlo=-5.0, sharplo=0.0, sharphi=2.0)
daogroup = DAOGroup(2.0*sigma_psf*gaussian_sigma_to_fwhm)
mmm_bkg = MMMBackground()
fitter = LevMarLSQFitter()
psf_model = IntegratedGaussianPRF(sigma=sigma_psf)
photometry = IterativelySubtractedPSFPhotometry(finder=iraffind, group_maker=daogroup, bkg_estimator=mmm_bkg, psf_model=psf_model, fitter=LevMarLSQFitter(), niters=1, fitshape=(11,11))
result_tab = photometry(image=image)
residual_image = photometry.get_residual_image()
'''
plt.subplot(1, 2, 1)
plt.imshow(image, cmap='viridis', aspect=1, interpolation='nearest', origin='lower')
plt.title('Simulated data')
plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
plt.subplot(1 ,2, 2)
'''
residual_png = plt.figure("residual.png")
plt.imshow(residual_image, cmap='viridis', aspect=1, interpolation='nearest', origin='lower')
plt.title('Residual Image')
plt.colorbar(orientation='horizontal', fraction=0.046, pad=0.04)
plt.savefig("/Users/jacob975/Documents/tat_data/test/residual.png")
residual_png.show()

raw_input()

# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
