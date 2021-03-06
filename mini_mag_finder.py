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

def SExtractor(image_name):
    # Initilized
    config_name = "{0}.config".format(image_name[:-5])
    catalog_name = "{0}.cat".format(image_name[:-5])
    # Copy parameter files to working directory.
    os.system('cp {0}/SE_workshop/SE.config {1}'.format(TAT_env.path_of_code, config_name))
    os.system("sed -i 's/stack_image/{0}/g' {1}".format(image_name[:-5], config_name))
    # Execute SExtrctor
    os.system('sex {0} -c {1}'.format(image_name, config_name))
    # Load the result table
    table = np.loadtxt(catalog_name)
    return table

def show_mini_mag(se_table, VERBOSE = 0):
    # Load the index of columes
    index_mag = TAT_env.SE_table_titles.index('MAG_AUTO')
    index_x = TAT_env.SE_table_titles.index('X_IMAGE')
    index_y = TAT_env.SE_table_titles.index('Y_IMAGE')
    # Take the minimum magnitude in INST_MAG 
    mag = se_table[:,index_mag]
    mini_mag = np.amax(mag)
    if VERBOSE > 0:print 'instrumental minimum mag: {0}'.format(mini_mag)
    xcenter = se_table[:,index_x]
    ycenter = se_table[:,index_y]
    reduce_data = np.transpose(np.array([mag, xcenter, ycenter]))
    reduce_data = reduce_data[mag.argsort()]
    # Pick 10 brightest stars from the data
    reduce_data = reduce_data[:50]
    pixcrd = reduce_data[:,1:]
    try: 
        header_wcs = pyfits.getheader("stacked_image.wcs")
    except:
        print "WCS not found"
        return 1, None
    w = wcs.WCS(header_wcs)
    world = w.wcs_pix2world(pixcrd, 1)
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
    se_table = SExtractor(image_name)
    failure, app_mag, app_mini_mag = show_mini_mag(se_table)
    numbers, bin_edges = np.histogram(app_mag, bins = np.linspace(10, 20, 41))
    bins = bin_edges[1:]
    index_max = np.argmax(numbers)
    print('limiting magnitude = {0}'.format(bins[index_max]))
    # Save the result to a file
    result = np.loadtxt('minimag_result.txt', dtype = str)
    result = np.append(result, [image_name, bins[index_max]])
    result = np.reshape(result, (-1, 2))
    np.savetxt('minimag_result.txt', result, fmt = '%s')
    # plot the histogram of magnitude
    plt.title(image_name)
    plt.plot(bins, numbers, c = 'r')
    plt.bar(bins, numbers, width = 0.2, color= 'b')
    plt.xlabel('CATA MAG')
    plt.ylabel("# of sources")
    plt.xlim(10, 20)
    plt.legend()
    plt.savefig('{0}_hist.png'.format(image_name[:-5]))
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
