#!/usr/bin/python
'''
Program:
    This is a program to find stars with IRAFstarfinder 
    Then save a target on frames table
Usage: 
    starfinder.py [image_list]
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
import TAT_env

# find a star through iraf finder
def starfinder(image_name):
    infos = image_info(image_name)
    mean_bkg = infos.bkg
    std_bkg = infos.std
    sigma = infos.sigma
    iraffind = IRAFStarFinder(threshold = 5.0*std_bkg + mean_bkg, \
                            fwhm = sigma*gaussian_sigma_to_fwhm, \
                            minsep_fwhm = 2, \
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
    column_names = TAT_env.titles_for_target_on_iraf_table
    column_mod_names = TAT_env.titles_for_target_on_frame_table 
    iraf_mod_table = []
    # Convert table into 2D np.array
    for name in column_names:
        iraf_mod_table.append(np.array(iraf_table[name]))
    iraf_mod_table = np.array(iraf_mod_table)
    iraf_mod_table = np.transpose(iraf_mod_table)
    # Get WCS infos with astrometry
    failure, header_wcs = load_wcs()
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
    iraf_mod_table = np.array(iraf_mod_table, dtype = object)
    # Name targets with RA and DEC, and insert into table
    table_length = len(world[0])
    target_names_list = np.array(["target_{0}_{1}".format(world[0,i], world[1,i]) for i in range(table_length)]) 
    iraf_mod_table = np.insert(iraf_mod_table, 1, target_names_list, axis=1)
    # Move flux and mag to number 3 and 4.
    iraf_mod_table = np.insert(iraf_mod_table, 2, np.array(iraf_table['flux']), axis = 1)
    iraf_mod_table = np.insert(iraf_mod_table, 3, np.array(iraf_table['mag']), axis = 1)
    # delete the duplicated column  on the back.
    iraf_mod_table = np.delete(iraf_mod_table, -1, 1)
    iraf_mod_table = np.delete(iraf_mod_table, -1, 1)
    #------------------------------------------------------
    # Insert infos from images
    # load infos from the header of the image
    header = pyfits.getheader(image_name) 
    filename = np.repeat(image_name, table_length)
    filepath = os.getcwd()
    filepath = np.repeat(filepath, table_length)
    filter_ = np.repeat(header['FILTER'], table_length)
    try:
        sitename = np.repeat(header['OBSERVAT'], table_length)
    except:
        sitename = np.repeat(header['LOCATION'], table_length)
    exptime = np.repeat(header['EXPTIME'], table_length)
    date_obs = np.repeat(header['DATE-OBS'], table_length)
    time_obs = np.repeat(header['TIME-OBS'], table_length)
    mjd = np.repeat(header['MJD-OBS'], table_length)
    airmass = np.repeat(header['AIRMASS'], table_length)
    jd = np.repeat(header['JD'], table_length)
    hjd = np.repeat(header['HJD'], table_length)
    bjd = np.repeat(header['BJD'], table_length)
    # append those column into the table
    iraf_mod_table = np.insert(iraf_mod_table, -1, filename, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, filepath, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, filter_, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, sitename, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, exptime, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, date_obs, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, time_obs, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, mjd, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, airmass, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, jd, 1)
    iraf_mod_table = np.insert(iraf_mod_table, -1, hjd, 1)
    iraf_mod_table = np.insert(iraf_mod_table,  2, bjd, 1)
    iraf_mod_table = np.insert(iraf_mod_table, 14, iraf_mod_table[:,-1], 1)
    iraf_mod_table = np.delete(iraf_mod_table, -1, 1)
    # Insert titles
    iraf_mod_table = np.insert(iraf_mod_table, 0, column_mod_names, axis=0)
    return 0, iraf_mod_table, column_names

def load_wcs():
    # Load the file
    try:
        header_wcs = pyfits.getheader("stacked_image.wcs")
    except:
        print "WCS not found" 
        return 1, None
    return 0, header_wcs

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    if len(argv) != 2:
        print "Error! Wrong argument"
        print "Usage: starfinder.py [images list]"
        exit(1)
    name_image_list = argv[1]
    image_list = np.loadtxt(name_image_list, dtype = str)
    #----------------------------------------
    # PSF register
    for image_name in image_list:
        iraf_table, infos = starfinder(image_name)
        failure, iraf_mod_table, column_names = iraf_tbl_modifier(image_name, iraf_table)
        region = iraf_tbl2reg(iraf_table)
        # Save iraf table and region file
        np.savetxt("{0}.dat".format(image_name[:-5]), iraf_mod_table, fmt="%s")
        np.savetxt("{0}.reg".format(image_name[:-5]), region)
        os.system("ls *.dat > table_list")
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
