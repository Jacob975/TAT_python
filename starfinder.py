#!/usr/bin/python
'''
Program:
    This is a program to do psf register 
Usage: 
    starfinder.py [image_name]
Editor:
    Jacob975
20180626
#################################
update log

20180626 version alpha 1
    1. The code works
'''
import os 
from photutils.detection import IRAFStarFinder, DAOStarFinder
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.io import fits as pyfits
from fit_lib import get_peak_filter, get_star, hist_gaussian_fitting
from reduction_lib import image_info
import numpy as np
import time
from sys import argv

# find a star through iraf finder
def starfinder(name_image):
    infos = image_info(name_image)
    mean_bkg = infos.bkg
    std_bkg = infos.std
    sigma = infos.sigma
    iraffind = IRAFStarFinder(threshold = 5.0*std_bkg + mean_bkg, \
                            fwhm = sigma*gaussian_sigma_to_fwhm, \
                            minsep_fwhm = 0.5, \
                            roundhi = 1.0, \
                            roundlo = -1.0, \
                            sharplo = 0.5, \
                            sharphi = 2.0)
    iraf_table = iraffind.find_stars(infos.data)
    return iraf_table, infos

def iraf_tbl2reg(iraf_table):
    # create a region file from iraf table
    x = np.array(iraf_table['xcentroid'])
    y = np.array(iraf_table['ycentroid'])
    region = np.stack((x, y))
    region = np.transpose(region)
    return region

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    if len(argv) != 2:
        print "Error! Wrong argument"
        print "Usage: starfinder.py [image_name]"
        exit()
    name_image = argv[1]
    #----------------------------------------
    # PSF register
    iraf_table, infos = starfinder(name_image)
    region = iraf_tbl2reg(iraf_table)
    #---------------------------------------
    # Save iraf table and region file
    np.savetxt("{0}_pr.txt".format(name_image[:-5]), iraf_table)
    np.save("{0}_pr.npy".format(name_image[:-5]), iraf_table)
    np.savetxt("{0}_pr.reg".format(name_image[:-5]), region)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
