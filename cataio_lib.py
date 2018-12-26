#!/usr/bin/python
'''
Program:
    This is a program for correlating instrument magnitude and apparent magnitude in catalog  
Usage: 
    cataio_lib.py [table list]
Editor:
    Jacob975
20180805
#################################
update log
20180805 version alpha 1
    1. The code works
20180918 version alpha 2
    1. Name is changed. correlate_mag ---> cataio_lib, means catalog I/O library.
20180919 version alpha 3
    1. Rename a Def, correlate_mag ---> ensemble_photometry
20181204 version alpha 4
    1. Remove all photometries, and move to photometry_lib.py
'''
import numpy as np
import time
from sys import argv
from astropy import coordinates, units as u
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier
from register_lib import get_rid_of_exotic 
import TAT_env
from joblib import Parallel, delayed

# Get catalog with Vizier
def get_catalog(RA, DEC, column_names, catalog_index, VERBOSE = 0):
    # Match stars with catalog I/329
    try:
        if VERBOSE == 1: print "send a query to Vizier..."
        result = Vizier.query_region(coordinates.SkyCoord(ra=RA, dec=DEC, unit=('deg','deg'), frame='icrs'), 
                                    radius="10s", 
                                    catalog=[catalog_index])[0]
        if VERBOSE == 1: print "query finished"
    except:
        print "empty table"
        return 1, None
    distance_list = get_distance(result, column_names, RA, DEC)
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
def get_distance(match_stars, column_names, RA, DEC):
    distance_list = [] 
    for star in match_stars:
        try:
            match_ra = float(star[column_names.index('RAJ2000')])
            match_dec = float(star[column_names.index('DEJ2000')])
        except:
            c = SkyCoord(star[column_names.index('RAJ2000')], star[column_names.index('DEJ2000')], unit=(u.hourangle, u.deg))
            match_ra = c.ra.degree
            match_dec = c.dec.degree
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
    Vmag = float(match_star[12])
    gmag = float(match_star[13])
    rmag = float(match_star[14])
    imag = float(match_star[15])
    if filter_ == "A":
        return 1, None
    elif filter_ == "C":
        return 1, None
    #elif filter_ == "V" and gmag != 0 and rmag != 0:
    #    Vmag = gmag - 0.565 * (gmag - rmag) - 0.016
    #    return 0, Vmag
    elif filter_ == "V" and ~np.isnan(Vmag):
        return 0, Vmag
    elif filter_ == "R" and rmag != 0 and imag != 0:
        Rmag = rmag - 0.153 * (rmag - imag) - 0.117
        return 0, Rmag
    elif filter_ == "N" and gmag != 0 and rmag != 0: 
        return 1, None
    elif filter_ == "B" and gmag != 0 and rmag != 0:
        Bmag = gmag + 0.313 * (gmag - rmag) + 0.219
        return 0, Bmag
    else:
        return 1, None

# Find the alias, and spectral type of sources.
def find_alias_and_spectral_type(source):
    #-------------------------------------------------
    # Find the info of the source from HIC
    failure, match_star = get_catalog(source, TAT_env.HIC, TAT_env.index_HIC) 
    if failure:
        print "No corresponding band on catalog HIP" 
        source[2] = ''
        source[9] = ''
        return 1, source
    # Add alias and spectral type to the found source
    else:
        alias = 'HIC{0}'.format(match_star[0])
        spectral_type = match_star[TAT_env.HIC.index('Sp')]
    source[2] = alias
    source[9] = spectral_tyep
    return 0, source
