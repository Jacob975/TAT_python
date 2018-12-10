#!/usr/bin/python
'''
Program:
    This is a program for finding the minimum magnitude of source found in the image. 
Usage: 
    mini_mag_finder.py [image_list]
Editor:
    Jacob975
20181205
#################################
update log

20181205 version alpha 1:
    1. The code works.
'''
from photutils.detection import IRAFStarFinder
from astropy.stats import gaussian_sigma_to_fwhm
from astropy.io import fits as pyfits
from astropy import wcs
from astropy.coordinates import SkyCoord
from astropy import units as u
from reduction_lib import image_info
import numpy as np
import time
from sys import argv
import TAT_env
from cataio_lib import get_catalog, get_distance, get_app_mag
from reduction_lib import get_rid_of_exotic
from matplotlib import pyplot as plt

# find a star through iraf finder
def starfinder(image_name):
    infos = image_info(image_name)
    mean_bkg = infos.bkg
    std_bkg = infos.std
    u_sigma = infos.u_sigma
    sigma = u_sigma.n
    iraffind = IRAFStarFinder(threshold = 3.0*std_bkg + mean_bkg, \
                            # fwhm = sigma*gaussian_sigma_to_fwhm, \
                            fwhm = 2.2, \
                            minsep_fwhm = 2, \
                            roundhi = 1.0, \
                            roundlo = -1.0, \
                            sharplo = 0.5, \
                            sharphi = 2.0)
    iraf_table = iraffind.find_stars(infos.data)
    return iraf_table, infos

def show_mini_mag(iraf_table, infos, VERBOSE = 0):
    # Take the minimum magnitude in INST_MAG 
    mag = np.array(iraf_table['mag'])
    mini_mag = np.amax(mag)
    print 'instrumental minimum mag: {0}'.format(mini_mag)
    xcenter = np.array(iraf_table['xcentroid'])
    ycenter = np.array(iraf_table['ycentroid'])
    reduce_data = np.transpose(np.array([mag, xcenter, ycenter]))
    reduce_data = reduce_data[mag.argsort()]
    # Pick 10 brightest stars from the data
    reduce_data = reduce_data[:10]
    pixcrd = reduce_data[:,1:]
    try: 
        header_wcs = pyfits.getheader("stacked_image.wcs")
    except:
        print "WCS not found"
        return 1, None
    w = wcs.WCS(header_wcs)
    world = w.wcs_pix2world(pixcrd, 1)
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
    app_mini_mag = mini_mag + median_mag_delta
    return 0, app_mag, app_mini_mag

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Initialize
    if len(argv) != 2:
        print "Error!\n The number of arguments is wrong."
        print "Usage: mini_mag_finder.py [images name]"
        exit(1)
    image_name = argv[1]
    #----------------------------------------
    # Find all stars with IRAFstarfinder
    print ('--- mimi mag finder ---')
    print ('Image: {0}'.format(image_name))
    iraf_table, infos = starfinder(image_name)
    failure, app_mag, app_mini_mag = show_mini_mag(iraf_table, infos)
    numbers, bin_edges = np.histogram(app_mag, bins = np.linspace(10, 20, 51))
    bins = bin_edges[1:]
    index_max = np.argmax(numbers)
    print('limiting magnitude = {0}'.format(bins[index_max]-0.1))
    # plot the histogram of magnitude
    '''
    plt.title(image_name)
    plt.bar(bins, numbers)
    plt.plot([app_mini_mag, app_mini_mag], [0, 1], label = 'minimum magnitude')
    plt.xlabel('CATA MAG')
    plt.ylabel("# of sources")
    plt.legend()
    plt.show() 
    '''
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
