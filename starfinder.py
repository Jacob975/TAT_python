#!/usr/bin/python
'''
Program:
    This is a program to find stars with astrometry and IRAFstarfinder 
    And update the header with wcs
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
from photutils.detection import IRAFStarFinder, DAOStarFinder
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.io import fits as pyfits
from astropy import wcs
from fit_lib import get_peak_filter, get_star, hist_gaussian_fitting
from reduction_lib import image_info
import numpy as np
import time
import os
from sys import argv

# find a star through iraf finder
def starfinder(image_name):
    infos = image_info(image_name)
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

def iraf_tbl_modifier(image_name, iraf_table):
    # Initialize Variables
    column_names = ['id', 'xcentroid', 'ycentroid', 'fwhm', 'sharpness', 'roundness', 'pa', 'npix', 'sky', 'peak', 'flux', 'mag']
    column_mod_names = ['id', 'Name', 'RA', 'DEC', 'xcentroid', 'ycentroid', 'fwhm', 'sharpness', 'roundness', 'pa', 'npix', 'sky', 'peak', 'flux', 'mag']
    iraf_mod_table = []
    # Convert table into 2D np.array
    for i, name in enumerate(column_names):
        iraf_mod_table.append(np.array(iraf_table[name]))
    iraf_mod_table = np.array(iraf_mod_table)
    iraf_mod_table = np.transpose(iraf_mod_table)
    # Get WCS infos with astrometry
    failure, header_wcs = get_header_wcs(image_name)
    if failure:
        print "WCS not found"
        return 1, None, None
    w = wcs.WCS(header_wcs)
    # Convert pixel coord to RA and DEC
    pixcrd = np.array([np.array(iraf_table['xcentroid']), np.array(iraf_table['ycentroid'])])
    pixcrd = np.transpose(pixcrd)
    world = w.wcs_pix2world(pixcrd, 1)
    world = np.transpose(world)
    # Insert RA and DEC into np.array
    iraf_mod_table = np.insert(iraf_mod_table, 1, world, axis=1)
    # Convert dtype to str for saveing conveniently
    iraf_mod_table = np.array(iraf_mod_table, dtype = str)
    # name this target with RA and DEC, and insert
    target_names_list = np.array(["target_{0}_{1}".format(world[0,i], world[1,i]) for i in range(len(world[0]))]) 
    iraf_mod_table = np.insert(iraf_mod_table, 1, target_names_list, axis=1)
    # inserting titles
    iraf_mod_table = np.insert(iraf_mod_table, 0, column_mod_names, axis=0)
    return 0, iraf_mod_table, column_names

# Get WCS with astrometry programy
def get_header_wcs(image_name):
    try:
        # Load if existing already.
        header_wcs = pyfits.getheader("{0}.wcs".format(image_name[:-5]))
    except:
        astrometry_program = "/opt/astrometry/bin/solve-field"
        # Produce wcs header with astrometry
        command = "{0} {1} --overwrite".format(astrometry_program, image_name)
        os.system(command)
        # Load the file
        try:
            header_wcs = pyfits.getheader("{0}.wcs".format(image_name[:-5]))
        except:
            print "solve-field fail, no wcs reference."
            return 1, None
    return 0, header_wcs

def clean_astrometry_product():
    command = 'rm -f *.axy *.corr *.png *.xyls *.match *.rdls *.solved *.wcs'
    os.system(command)

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
    image_name = argv[1]
    #----------------------------------------
    # PSF register
    iraf_table, infos = starfinder(image_name)
    failure, iraf_mod_table, column_names = iraf_tbl_modifier(image_name, iraf_table)
    region = iraf_tbl2reg(iraf_table)
    command = 'mv {0}.new {0}_w.fits'.format(image_name[0:-5])
    os.system(command)
    # Save iraf table and region file
    np.savetxt("{0}.dat".format(image_name[:-5]), iraf_mod_table, fmt="%s")
    np.savetxt("{0}.reg".format(image_name[:-5]), region)
    # Clean synthetic files
    clean_astrometry_product()
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
