#!/usr/bin/python
'''
Program:
    This is a program for finding the minimum magnitude of source found in the image. 
Usage: 
    plot_d_mag.py [image_list]
Editor:
    Jacob975
20181219
#################################
update log

20181219 version alpha 1:
    1. The code works.
'''
from astropy.io import fits as pyfits
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np
import time
from sys import argv
import TAT_env
from cataio_lib import get_catalog, get_distance, get_app_mag
from reduction_lib import get_rid_of_exotic
from matplotlib import pyplot as plt
import os
from photometry import take_data_within_duration
import collections

def show_cata_mag(mag, ra, dec, VERBOSE = 1):
    # Load the index of columes
    reduce_data = np.transpose(np.array([mag, ra, dec], dtype = float))
    reduce_data = reduce_data[mag.argsort()]
    reduce_data = reduce_data[~np.isnan(reduce_data[:,0])]
    # Pick 50 brightest stars from the data
    reduce_data = reduce_data[:20]
    world = reduce_data[:,1:]
    #--------------------------------------------------
    # Find the catalog magnitude.
    # Query data from vizier
    mag_delta_list = []
    filter_ = 'V'
    for i in xrange(len(reduce_data)):
        inst_mag = reduce_data[i,0] 
        RA = float(world[i, 0])
        DEC = float(world[i, 1])
        failure, match_star = get_catalog(RA, DEC, TAT_env.URAT_1, TAT_env.index_URAT_1)
        if failure:
            continue
        failure, app_mag = get_app_mag(match_star, filter_)
        if failure:
            continue
        if np.isnan(inst_mag):
            continue
        mag_delta = app_mag - inst_mag
        if VERBOSE == 1: print "INST_MAG = {0}, CATA_MAG = {1}, delta = {2}".format(inst_mag, app_mag, mag_delta)
        mag_delta_list.append(mag_delta)
    # Find the average of delta_mag
    # Check if the number of source is enough or not.
    if len(mag_delta_list) == 0:
        print "No enough source found in catalogue for comparison"
        return 1
    mag_delta_list = get_rid_of_exotic(mag_delta_list)
    if len(mag_delta_list) < 3:
        print "No enough source found in catalogue for comparison"
        return 1
    # remove np.nan
    mag_delta_array = np.array(mag_delta_list)
    mag_delta_array = mag_delta_array[~np.isnan(mag_delta_array)]
    # Find the median of the delta of the magnitude, and apply the result on all sources.
    median_mag_delta = np.median(mag_delta_array)
    app_mag = mag + median_mag_delta
    return 0, app_mag

def pick_median(app_mag, err_app_mag):
    cata_mag = np.linspace(9, 20, 45)
    cata_mag = (cata_mag[1:] + cata_mag[:-1]) / 2.0
    lim_err_mag = np.zeros(len(cata_mag))
    for i, mag in enumerate(cata_mag):
        index = np.where(   (app_mag >= mag - 0.125 ) & 
                            (app_mag <  mag + 0.125))
        selected_err_app_mag = err_app_mag[index]
        lim_err_mag[i] = np.median(selected_err_app_mag)
    index_min_err_mag = np.nanargmin(lim_err_mag)
    lim_err_mag[:index_min_err_mag] = lim_err_mag[index_min_err_mag]
    nans, x= nan_helper(lim_err_mag)
    lim_err_mag[nans]= np.interp(x(nans), x(~nans), lim_err_mag[~nans])
    return cata_mag, lim_err_mag

def nan_helper(y):
    """Helper to handle indices and logical indices of NaNs.

    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
            to convert logical indices of NaNs to 'equivalent' indices
    Example:
        >>> # linear interpolation of NaNs
        >>> nans, x= nan_helper(y)
        >>> y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    """
    return np.isnan(y), lambda z: z.nonzero()[0]

def observable_kepler(cata_mag, lim_err_mag, kepler_mag, kepler_depth):
    num_observable_sources = np.zeros(len(cata_mag))
    for i, mag in enumerate(cata_mag):
        index = np.where(   (kepler_mag >= mag - 0.125 ) & 
                            (kepler_mag < mag + 0.125) & 
                            (kepler_depth > lim_err_mag[i]))
        num_observable_sources[i] = len(index[0])
    return cata_mag, num_observable_sources
#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    if len(argv) != 4:
        print "Error!\n The number of arguments is wrong."
        print "Usage: plot_d_mag.py [start time] [end time]"
        exit(1)
    start_date = argv[1]
    end_date = argv[2]
    transit_table_name = argv[3]
    #----------------------------------------
    # Processing
    print ('---plot d mag ---')
    # Take the data in this duration
    data = take_data_within_duration(start_date, end_date)
    # Load the index
    index_BJD = TAT_env.obs_data_titles.index("BJD") 
    index_INST_MAG = TAT_env.obs_data_titles.index('INST_MAG')
    index_E_INST_MAG = TAT_env.obs_data_titles.index('E_INST_MAG')
    index_EP_MAG = TAT_env.obs_data_titles.index('EP_MAG')
    index_E_EP_MAG = TAT_env.obs_data_titles.index('E_EP_MAG')
    index_RA = TAT_env.obs_data_titles.index('RA')
    index_DEC = TAT_env.obs_data_titles.index('`DEC`')
    # Find the first image
    all_bjd = data[:,index_BJD]
    bjd_s = [item for item, count in collections.Counter(all_bjd).items() if count > 1]
    first_bjd = np.amin(bjd_s)
    # Take and analyize the data of the first image.
    first_frame_data = data[data[:,index_BJD] == first_bjd]
    ep_mag = np.array(first_frame_data[:, index_EP_MAG], dtype = float)
    e_ep_mag = np.array(first_frame_data[:, index_E_EP_MAG], dtype = float)
    index_no_nan_in_ep_mag = np.where(~np.isnan(ep_mag) & ~np.isnan(e_ep_mag))
    ra = first_frame_data[:, index_RA]
    dec = first_frame_data[:, index_DEC]
    ep_mag = ep_mag[index_no_nan_in_ep_mag]
    e_ep_mag = e_ep_mag[index_no_nan_in_ep_mag]
    ra = ra[index_no_nan_in_ep_mag]
    dec = dec[index_no_nan_in_ep_mag]
    failure, app_mag = show_cata_mag(ep_mag, ra, dec)
    # Load transit table
    index_Vmag = 11
    index_depth = 10
    index_depth_measure = 9
    index_DEC = 5
    transit_table = np.loadtxt(transit_table_name, dtype = str, delimiter = '\t')
    transit_table = transit_table[1:]
    # Ignore all no-observed data
    transit_table = transit_table[transit_table[:,index_Vmag] != '']
    # Take data
    Vmag = np.array(transit_table[:,index_Vmag], dtype = float)
    depth = np.array(transit_table[:,index_depth], dtype = float)
    depth_measure = np.array(transit_table[:,index_depth_measure], dtype = str)
    DEC = np.array(transit_table[:, index_DEC], dtype = float)
    above_south30 = DEC > -30.
    
    # Take source above -30 dec
    Vmag  = Vmag[above_south30]
    depth = depth[above_south30]
    depth_measure = depth_measure[above_south30]
    
    depth_measure[depth_measure == ''] = '0.0'
    depth_measure = np.array(depth_measure, dtype = float)
    where_no_depth = depth == 0.0
    depth[where_no_depth] = depth_measure[where_no_depth]
    depth = depth / 100.
    # Calculate the histogram
    numbers, bin_edges = np.histogram(Vmag, bins = np.linspace(9, 20, 45))
    bins = (bin_edges[1:] + bin_edges[:-1]) / 2.0
    cata_mag, lim_err_mag = pick_median(app_mag, e_ep_mag)
    _, num_obs_source = observable_kepler(cata_mag, lim_err_mag, Vmag, depth)
    print np.sum(numbers)
    print np.sum(num_obs_source)
    # plot the histogram of magnitude
    fig, axs = plt.subplots(1, 1, figsize = (8,6))
    axs.set_title('The observable transits')
    axs.bar(bins, numbers, width = 0.25, color = 'b', label = 'Comfirm transits')
    axs.bar(cata_mag, num_obs_source, width = 0.20, color = 'r', label = 'Observable comfirm transits')
    axs.set_xlabel('V magnitude')
    axs.set_ylabel("# of sources")
    axs.set_xlim(9, 20)
    axs.grid()
    axs.legend()
    plt.savefig('{0}_{1}_hist_kepler.png'.format(start_date, end_date))
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
