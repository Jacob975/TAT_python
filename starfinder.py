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
from photutils.detection import IRAFStarFinder, DAOStarFinder
from photutils import aperture_photometry, CircularAperture
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.io import fits as pyfits
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy import units as u
from fit_lib import get_star, get_peak_filter, get_flux
from reduction_lib import image_info
from mysqlio_lib import save2sql, find_fileID, find_source_match_coords
import matplotlib.pyplot as plt
import numpy as np
import time
import os
from sys import argv
import TAT_env
from test_EP import flux2mag

# find a star through iraf finder
def starfinder(image_name):
    infos = image_info(image_name)
    mean_bkg = infos.bkg
    std_bkg = infos.std
    u_sigma = infos.u_sigma
    sigma = u_sigma.n
    print 3.0*std_bkg + mean_bkg
    iraffind = IRAFStarFinder(threshold = 3.0*std_bkg + mean_bkg, \
                            # fwhm = sigma*gaussian_sigma_to_fwhm, \
                            fwhm = 5.0,
                            roundhi = 1.0, 
                            roundlo = -1.0,
                            sharphi = 2.0,
                            sharplo = 0.5)
    iraf_table = iraffind.find_stars(infos.data)
    return iraf_table, infos

def star_phot(image_name, iraf_table, infos):
    # Initialize Variables
    iraf_table_titles = TAT_env.iraf_table_titles
    extend_star_table_titles = TAT_env.extend_star_table_titles
    coord = np.array([np.array(iraf_table['ycentroid']), np.array(iraf_table['xcentroid'])], dtype = int)
    coord = np.transpose(coord)
    #------------------------------------------------------------
    # Redo the flux measurements.
    try:
        image = pyfits.getdata(image_name)
        star_array = get_flux(image, coord, infos.u_sigma_x, infos.u_sigma_y)
        # Replace all inf value by -999
        star_array[np.isinf(star_array)] = -999
        extend_star_array = np.full((len(star_array), len(extend_star_table_titles)), None, dtype = object)
    except:
        return 1, None
    #------------------------------------------------------------
    # Add infomations into the extend star array
    # Get WCS infos with astrometry
    try:
        header_wcs = pyfits.getheader("stacked_image.wcs")
    except:
        print "WCS not found"
        return 1, None, None
    w = wcs.WCS(header_wcs)
    # Convert pixel coord to RA and DEC
    pixcrd = np.transpose(np.array([star_array[:,6], star_array[:,4]]))
    world = w.wcs_pix2world(pixcrd, 1)
    # RA and DEC
    extend_star_array[:,14] = world[:,0]
    extend_star_array[:,15] = world[:,1]
    # Name targets with RA and DEC, and insert into table
    table_length = len(world)
    target_names_list = np.array(["target_{0:.4f}_{1:.4f}".format(world[i,0], world[i,1]) for i in range(table_length)]) 
    # NAME
    extend_star_array[:,1] = target_names_list
    # FLUX
    extend_star_array[:,4] = star_array[:,0]
    extend_star_array[:,5] = star_array[:,1]
    # INST MAG
    mag, err_mag = flux2mag(star_array[:,0], star_array[:,1])
    extend_star_array[:,6] = mag
    extend_star_array[:,7] = err_mag
    # AMP
    extend_star_array[:,17] = star_array[:,2]
    extend_star_array[:,18] = star_array[:,3]
    # CENTER
    extend_star_array[:,19] = star_array[:,6]
    extend_star_array[:,20] = star_array[:,4]
    # SIGMA
    extend_star_array[:,21] = star_array[:,10]
    extend_star_array[:,22] = star_array[:,11]
    extend_star_array[:,23] = star_array[:,8]
    extend_star_array[:,24] = star_array[:,9]
    # PA
    extend_star_array[:,25] = star_array[:,12]
    extend_star_array[:,26] = star_array[:,13]
    # SKY
    extend_star_array[:,27] = star_array[:,14]
    extend_star_array[:,28] = star_array[:,15]
    # NPIX
    extend_star_array[:,29] = star_array[:,16]
    # Load infos from the header of the image
    header = pyfits.getheader(image_name) 
    # get the fileID from mysql.
    fileID = find_fileID(image_name)
    # The else
    extend_star_array[:,  3] = header['BJD']
    extend_star_array[:, 30] = header['JD']
    extend_star_array[:, 31] = header['MJD-OBS']
    extend_star_array[:, 32] = header['HJD']
    extend_star_array[:, 33] = fileID
    np.savetxt('wcs_coord.txt', world)
    return 0, extend_star_array

def star_extend(image_name, SE_table):
    #------------------------------------------------------------
    # Add infomations into the extend star array
    # Get WCS infos with astrometry
    try:
        header_wcs = pyfits.getheader("stacked_image.wcs")
    except:
        print "WCS not found"
        return 1, None, None
    w = wcs.WCS(header_wcs)
    # Convert pixel coord to RA and DEC
    pixcrd = np.transpose(np.array([SE_table[:,2], SE_table[:,3]]))
    world = w.wcs_pix2world(pixcrd, 1)
    extend_star_array = np.full((len(SE_table), len(TAT_env.extend_star_table_titles)), None, dtype = object)
    # RA and DEC
    extend_star_array[:,14] = world[:,0]
    extend_star_array[:,15] = world[:,1]
    # Name targets with RA and DEC, and insert into table
    table_length = len(world)
    target_names_list = np.array(["target_{0:.4f}_{1:.4f}".format(world[i,0], world[i,1]) for i in range(table_length)]) 
    # NAME
    extend_star_array[:,1] = target_names_list
    # FLUX
    extend_star_array[:,4] = SE_table[:,6]
    extend_star_array[:,5] = SE_table[:,7]
    # INST MAG
    extend_star_array[:,6] = SE_table[:,4]
    extend_star_array[:,7] = SE_table[:,5]
    # CENTER
    extend_star_array[:,19] = SE_table[:,2]
    extend_star_array[:,20] = SE_table[:,3]
    # Load infos from the header of the image
    header = pyfits.getheader(image_name) 
    # get the fileID from mysql.
    fileID = find_fileID(image_name)
    # The else
    extend_star_array[:,  3] = header['BJD']
    extend_star_array[:, 30] = header['JD']
    extend_star_array[:, 31] = header['MJD-OBS']
    extend_star_array[:, 32] = header['HJD']
    extend_star_array[:, 33] = fileID
    return 0, extend_star_array

def SExtractor(image_name):
    # Initilized
    config_name = "{0}.config".format(image_name[:-5])
    catalog_name = "{0}.cat".format(image_name[:-5])
    index_flag = TAT_env.SE_table_titles.index('FLAGS')
    # Copy parameter files to working directory.
    os.system('cp {0}/SE_workshop/SE.config {1}'.format(TAT_env.path_of_code, config_name))
    os.system("sed -i 's/stack_image/{0}/g' {1}".format(image_name[:-5], config_name))
    # Execute SExtrctor
    os.system('sex {0} -c {1}'.format(image_name, config_name))
    # Load the result table
    table = np.loadtxt(catalog_name)
    table = table[table[:,index_flag ] == 0 ]
    return table

# check if there is new sources.
def check_new_sources(extend_star_array):
    # Initialize
    new_source_list = []
    new = False
    index_of_name = TAT_env.obs_data_titles.index('NAME')
    index_of_ra   = TAT_env.obs_data_titles.index('RA')
    index_of_dec  = TAT_env.obs_data_titles.index('`DEC`')
    # Setup the spatial tolerance.
    tolerance = TAT_env.pix1/3600.0 * 3.0
    # Match positions
    for i in xrange(len(extend_star_array)):
        src_coord_list = find_source_match_coords(  extend_star_array[i, index_of_ra],
                                                    extend_star_array[i, index_of_dec], 
                                                    tolerance)
        src_coord_array = np.asarray(src_coord_list)
        if src_coord_list == None:
            continue
        # No nearby sources found in databases imply that's a new source.
        if len(src_coord_list) == 0:
            new_source_list.append([extend_star_array[i, index_of_name],
                                    extend_star_array[i, index_of_ra],
                                    extend_star_array[i, index_of_dec]])
            continue
        
        stu = find_sources(src_coord_array, tolerance)
        failure, min_distance, jndex = stu.find([extend_star_array[i,index_of_ra], 
                                                extend_star_array[i,index_of_dec]]) 
        # Update the name if we found a existed observation from database.
        if not failure:
            extend_star_array[i, index_of_name] = src_coord_array[jndex, index_of_name]
        # Update the database if we don't.
        else :
            new_source_list.append([extend_star_array[i, index_of_name], 
                                    extend_star_array[i, index_of_ra],
                                    extend_star_array[i, index_of_dec]]) 
    # Check if we find new sources or not in this observations.
    if len(new_source_list) > 0:
        new = True
    return extend_star_array, new_source_list, new

# This is a class for match the coordinates efficiently.
class find_sources():
    def __init__(self, coord_table, tolerance = 0.0):
        self.coord_table = coord_table
        self.tolerance = tolerance
        self.ref_coords = SkyCoord(self.coord_table[:,2], self.coord_table[:,3], unit = 'deg')
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
def make_coord(src_list):
    index_RA = TAT_env.src_titles.index("RA")
    index_DEC = TAT_env.src_titles.index("`DEC`")
    ra_array = src_list[index_RA]
    dec_array= src_list[index_DEC]
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
        print ("{0}, start!".format(image_name))
        print ('SExtractor!')
        SE_table = SExtractor(image_name)
        failure, extend_star_array = star_extend(image_name, SE_table)
        # Create an parameter file.
        '''
        print ('--- starfinder ---')
        iraf_table, infos = starfinder(image_name)
        # Add more infos
        print ('--- star phot ---')
        failure, extend_star_array = star_phot(image_name, iraf_table, infos)
        if failure:
            print 'phot failure'
            continue
        '''
        # Rename if source is already named in previous observations.
        print ('--- repeatness check ---')
        extend_star_array, new_sources, new = check_new_sources(extend_star_array)
        # Save and upload the result
        save2sql(extend_star_array, new_sources, new)
        print ("done.")
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
