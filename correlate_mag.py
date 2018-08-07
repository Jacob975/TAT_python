#!/usr/bin/python
'''
Program:
    This is a program for correlating instrument magnitude and apparent magnitude in catalog  
Usage: 
    correlate_mag.py [table list]
Editor:
    Jacob975
20180805
#################################
update log
20180805 version alpha 1
    1. The code works
'''
import numpy as np
import time
from sys import argv
from astropy import coordinates, units as u
from astroquery.vizier import Vizier
from register_lib import get_rid_of_exotic 
import TAT_env

# Get catalog with Vizier
def get_catalog(targets):
    # initialize
    column_names = ['URAT1', 
                    'RAJ2000', 
                    'DEJ2000', 
                    'Epoch', 
                    'f.mag', 
                    'e_f.mag', 
                    'pmRA', 
                    'pmDE', 
                    'Jmag', 
                    'Hmag', 
                    'Kmag', 
                    'Bmag', 
                    'Vmag', 
                    'gmag', 
                    'rmag', 
                    'imag']
    RA = float(targets[5])
    DEC = float(targets[6])
    # Match stars with catalog I/329
    try:
        print "send a query to Vizier..."
        result = Vizier.query_region(coordinates.SkyCoord(ra=RA, dec=DEC, unit=('deg','deg'), frame='icrs'), 
                                    radius="10s", 
                                    catalog=["I/329"])[0]
        print "query finished"
    except:
        print "empty table"
        return 1, None
    distance_list = get_distance(result, RA, DEC)
    # Convert tuple to numpy array
    result_table = []
    for name in column_names:
        result_table.append(np.array(result[name]))
    result_table = np.array(result_table)
    result_table = np.transpose(result_table)
    # insert distance list into result
    result_table_with_distance = np.insert(result_table, 1, distance_list, axis = 1)
    # Sort by distance and pick the closet one
    result_table_with_distance = result_table_with_distance[result_table_with_distance[:,1].argsort()]
    return 0, result_table_with_distance[0]

# The program calculate the distance of match stars and our sources.
def get_distance(match_stars, RA, DEC):
    distance_list = [] 
    for star in match_stars:
        match_ra = float(star[1])
        match_dec = float(star[2])
        d_ra = abs(match_ra - RA)
        d_dec = abs(match_dec - DEC)
        distance = np.sqrt(np.power(d_ra, 2) + np.power(d_dec, 2))
        distance_list.append(distance)
    return distance_list

# return apparent magnitude based on filters.
def get_app_mag(match_star, filter_):
    '''
    extract R , I values from r and i magnitudes  (Jordi et al., 2006)
    B-g   =     (0.313 +/- 0.003)*(g-r)  + (0.219 +/- 0.002)
    V-g   =     (-0.565 +/- 0.001)*(g-r) - (0.016 +/- 0.001)
    V-I   =     (0.675 +/- 0.002)*(g-i)  + (0.364 +/- 0.002) if  g-i <= 2.1
    V-I   =     (1.11 +/- 0.02)*(g-i)    - (0.52 +/- 0.05)   if  g-i >  2.1
    R-r   =     (-0.153 +/- 0.003)*(r-i) - (0.117 +/- 0.003)
    R-I   =     (0.930 +/- 0.005)*(r-i)  + (0.259 +/- 0.002)
    '''
    gmag = float(match_star[13])
    rmag = float(match_star[14])
    imag = float(match_star[15])
    if filter_ == "A":
        return 1, None
    elif filter_ == "C":
        return 1, None
    elif filter_ == "V" and gmag != 0 and rmag != 0:
        Vmag = gmag - 0.565 * (gmag - rmag) - 0.016
        return 0, Vmag
    elif filter_ == "R" and rmag != 0 and imag != 0:
        Rmag = rmag - 0.153 * (rmag - imag) - 0.117
        return 0, Rmag
    # replace N with V
    elif filter_ == "N" and gmag != 0 and rmag != 0:
        Vmag = gmag - 0.565 * (gmag - rmag) - 0.016
        return 0, Vmag
    elif filter_ == "B" and gmag != 0 and rmag != 0:
        Bmag = gmag + 0.313 * (gmag - rmag) + 0.219
        return 0, Bmag
    else:
        return 1, None

# the def is used to correlate the magnitude with catalog
def correlate_mag(table):
    print "### start to correlate the inst mag to apparent mag in catalog I/329"
    # If filter is A or C, skip them
    filter_ = table[0,18]
    print "filter = {0}".format(filter_)
    if filter_ == "A" or filter_ == "C":
        print "No corresponding band on catalog I/329"
        table = np.insert(table, 5, 0.0, axis = 1)
        return 1, table
    # Choose the 10 brightest stars
    flux = np.array(table[:,3], dtype = float)
    flux_order_table = table[flux.argsort()]
    mag_delta_list = []
    for index in np.arange(-10, 0, 1):
        # Find the info of the source on the catalog
        failure, match_star = get_catalog(flux_order_table[index]) 
        if failure:
            continue
        # Find the apparent magnitude to the found source
        failure, app_mag = get_app_mag(match_star, filter_)
        if failure:
            continue
        inst_mag = float(flux_order_table[index, 4])
        mag_delta = app_mag - inst_mag
        print "inst_mag = {0}, app_mag = {1}, delta = {2}".format(inst_mag, app_mag, mag_delta)
        mag_delta_list.append(mag_delta)
    # Check if the number of source is enough or not.
    if len(mag_delta_list) == 0:
        print "No enough source found in catalogue for comparison"
        table = np.insert(table, 5, 0.0, axis = 1)
        return 1, table
    mag_delta_list = get_rid_of_exotic(mag_delta_list)
    if len(mag_delta_list) < 3:
        print "No enough source found in catalogue for comparison"
        table = np.insert(table, 5, 0.0, axis = 1)
        return 1, table
    # remove np.nan
    mag_delta_array = np.array(mag_delta_list)
    mag_delta_array = mag_delta_array[~np.isnan(mag_delta_array)]
    # Find the medina of magnitude delta, and apply the result on all sources.
    median_mag_delta = np.median(mag_delta_array)
    inst_mag_array = np.array(table[:, 4], dtype = float)
    app_mag_array = inst_mag_array + median_mag_delta
    app_mag_array = np.array(app_mag_array, dtype = object)
    table = np.insert(table, 5, app_mag_array, axis = 1)
    return 0, table

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print "Wrong number of arguments"
        print "Usage: correlate_mag.py [table list]"
        exit(1)
    table_name_list_name = argv[1]
    #----------------------------------------
    # Load table and find apparent magnitude in catalogs
    table_name_list = np.loadtxt(table_name_list_name, dtype = str)
    for table_name in table_name_list:
        # Load table
        print "### Load a table ###"
        table = np.loadtxt(table_name, dtype = object, skiprows = 1)
        failure, table = correlate_mag(table)
        if failure: 
            print "correlating fail"
            continue
        table = np.insert(table, 0, TAT_env.titles_for_target_on_frame_table, axis = 0)
        # Save table
        np.savetxt("{0}_a.dat".format(table_name[:-4]), table, fmt = "%s")
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
