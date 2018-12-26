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

def dmag2nsr(dmag):
    nsr = dmag/2.5 * np.log(10)
    return nsr

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    if len(argv) != 3:
        print "Error!\n The number of arguments is wrong."
        print "Usage: plot_d_mag.py [start time] [end time]"
        exit(1)
    start_date = argv[1]
    end_date = argv[2]
    #----------------------------------------
    # Processing
    print ('---plot d mag ---')
    # Take the data in this duration
    data = take_data_within_duration(start_date, end_date)
    # Load the index
    index_BJD = TAT_env.obs_data_titles.index("BJD") 
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
    err_ep_mag = first_frame_data[:, index_E_EP_MAG]
    ra = first_frame_data[:, index_RA]
    dec = first_frame_data[:, index_DEC]
    failure, app_mag = show_cata_mag(ep_mag, ra, dec)
    # plot the histogram of magnitude
    fig, axs = plt.subplots(1, 1, figsize = (8,6))
    axs.set_title('The relation between noise and signal')
    #plt.scatter(app_mag, flux_nsr, s = 2)
    axs.scatter(app_mag, err_ep_mag, s = 3, label = 'Vmag, exptime = 150 sec.')
    axs.set_xlabel('V magnitude')
    axs.set_ylabel("magnitude uncertainties")
    axs.set_xlim(10, 20)
    axs.set_ylim(1e-3, 1)
    axs.set_yscale('log')
    axs.grid(which = 'major', linestyle='-')
    axs.grid(which = 'minor', linestyle='--')
    for label in axs.yaxis.get_majorticklabels():
        label.set_fontsize(14)
    axs.legend()
    ax2 = axs.twinx()
    ax2.set_ylabel('noise-flux ratio')
    min_nsr = dmag2nsr(1e-3)
    max_nsr = dmag2nsr(1)
    ax2.set_ylim(min_nsr, max_nsr)
    ax2.set_yscale('log')
    for label in ax2.yaxis.get_majorticklabels():
        label.set_fontsize(14)
    plt.savefig('{0}_{1}_nsr.png'.format(start_date, end_date))
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
