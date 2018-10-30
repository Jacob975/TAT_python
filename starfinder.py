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
20181029 version alpha 2
    1. Make the program simplier, leave the func for finding source only.
        Anything else(IDP, EP) is independant from here.
'''
from photutils.detection import IRAFStarFinder
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.io import fits as pyfits
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy import units as u
from reduction_lib import image_info
from mysqlio_lib import save2sql, find_fileID, load_src_name_from_db
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

def iraf_tbl_modifier(image_name, iraf_table):
    # Initialize Variables
    iraf_mod_table = np.full((len(iraf_table), len(TAT_env.obs_data_titles)), None, dtype = object)
    iraf_table_titles = TAT_env.iraf_table_titles
    # Convert table into 2D np.array
    for infos in iraf_table_titles:
        iraf_mod_table[:,infos[1]] = np.array(iraf_table[infos[0]])
    # Get WCS infos with astrometry
    try:
        header_wcs = pyfits.getheader("stacked_image.wcs")
    except:
        print "WCS not found"
        return 1, None, None
    w = wcs.WCS(header_wcs)
    # Convert pixel coord to RA and DEC
    pixcrd = np.array([np.array(iraf_table['xcentroid']), np.array(iraf_table['ycentroid'])])
    pixcrd = np.transpose(pixcrd)
    world = w.wcs_pix2world(pixcrd, 1)
    iraf_mod_table[:,9] = world[:,0]
    iraf_mod_table[:,10] = world[:,1]
    # Name targets with RA and DEC, and insert into table
    table_length = len(world)
    target_names_list = np.array(["target_{0:.4f}_{1:.4f}".format(world[i,0], world[i,1]) for i in range(table_length)]) 
    iraf_mod_table[:,1] = target_names_list
    #------------------------------------------------------
    # Insert infos from images
    # Load infos from the header of the image
    header = pyfits.getheader(image_name) 
    # get the fileID from mysql.
    fileID = find_fileID(image_name)
    iraf_mod_table[:, 24] = fileID
    iraf_mod_table[:, 21] = header['MJD-OBS']
    iraf_mod_table[:, 22] = header['JD']
    iraf_mod_table[:, 23] = header['HJD']
    iraf_mod_table[:,  3] = header['BJD']
    return 0, iraf_mod_table

# check if there is new sources.
def check_new_sources(iraf_mod_table):
    # Initialize
    new_source_list = []
    new = False
    src_name_list = load_src_name_from_db()
    index_of_name = TAT_env.obs_data_titles.index('NAME')
    tolerance = TAT_env.pix1/3600.0 * 3.0
    src_coord_list = make_coord(src_name_list)
    stu = find_sources(src_coord_list, tolerance)
    # Match positions
    if len(src_name_list) != 0:
        for i in xrange(len(iraf_mod_table)):
            failure, min_distance, jndex = stu.find([iraf_mod_table[i,9], iraf_mod_table[i,10]])
            if not failure:
                iraf_mod_table[i, index_of_name] = src_name_list[jndex]
            else :
                new_source_list.append(iraf_mod_table[i, index_of_name])
    elif len(src_name_list) == 0:
        new_source_list = iraf_mod_table[:,index_of_name]
    # Test if we find new sources or not in this observation..
    if len(new_source_list) > 0:
        new = True
    return iraf_mod_table, new_source_list, new

# This is a class for match the coordinates efficiently.
class find_sources():
    def __init__(self, coord_table, tolerance = 0.0):
        self.coord_table = coord_table
        self.tolerance = tolerance
        self.ref_coords = SkyCoord(self.coord_table[:,0], self.coord_table[:,1], unit = 'deg')
        return
    def find(self, coord):
        source_coord = SkyCoord(coord[0], coord[1], unit = 'deg') 
        # Calculate the distance
        distance_object_array = self.ref_coords.separation(source_coord)
        distance_array = distance_object_array.deg
        # Pick the nearest one
        min_distance = np.min(distance_array)
        index_min_distance = np.argmin(distance_array) 
        if min_distance < self.tolerance:
            return False, min_distance, index_min_distance
        else:
            return True, 0.0, 0

# The def find the match name of target names.
def make_coord(src_name_list):
    index_RA = TAT_env.obs_data_titles.index("RA")
    index_DEC = TAT_env.obs_data_titles.index("`DEC`")
    ra_list = [None for i in src_name_list]
    dec_list = [None for i in src_name_list]
    for i, src_name in enumerate(src_name_list):
        name_list = src_name.split("_")
        ra_list[i]  = float(name_list[1])
        dec_list[i] = float(name_list[2])
    ra_array = np.array(ra_list)
    dec_array= np.array(dec_list)
    ans_array = np.transpose([ra_array, dec_array])
    return ans_array

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    if len(argv) != 2:
        print "Error!\n The number of arguments is wrong."
        print "Usage: starfinder.py [images list]"
        exit(1)
    name_image_list = argv[1]
    image_list = np.loadtxt(name_image_list, dtype = str)
    #----------------------------------------
    # PSF register
    for image_name in image_list:
        # Find all stars with IRAFstarfinder
        iraf_table, infos = starfinder(image_name)
        # Add extra infos
        failure, iraf_mod_table = iraf_tbl_modifier(image_name, iraf_table)
        # Rename if source is already named in previous observations.
        iraf_mod_table, new_sources, new = check_new_sources(iraf_mod_table)
        # Save and upload the result
        save2sql(iraf_mod_table, new_sources, new)
        print ("{0}, done.".format(image_name))
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
