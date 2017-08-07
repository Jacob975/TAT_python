#!/usr/bin/python
'''
Program:
This is a program to find the property of star on fits, including amplitude, position, beamsize, and bkg,
If you want,it can graph results out.
This program only can use on images.
method:
If you want to process lots of fits.
1. get_info.py [list name]

or If you only process a fits.
2. get_info.py [fits name]

You can controll the eccentricity of stars you found by option.
with default 0.9
3. get_info.py [eccentricity] [list name] 

e.g.    $get_info.py 0.7 some.fits      # eccentricity will be set as 0.7
        $get_info.py another.fits       # eccentricity will be set as default
        $get_info.py fits_list          # eccentricity will be set as default, and it will process a list of fits.

editor Jacob975
#################################
update log
    20170403 version alpha 1 
    the program can run properly

    20170422 version alpha 2
    now it can find the position of stars by gaussian 2D fitting.

    20170515 version alpha 3
    add a new func to print the property of stars on fits, including the amplitude, position, beamsize, and bkg
    It also print the mean of std after all task.

    20170702 version alpha 4
    change name from get_pos.py to get_info.py
    because previous name usually sounded confusing.

    20170705 version alpha 5
    1. the code will save star list found in each fits.
        data type is .tsv
    2. If you only want to process a data, you can just use fits name as argv.
        details is writed above.

    20170705 version alpha 6
    1.  add a new option to controll the eccentricity of stars.
    2.  add usage example of this code.

    20170720 version alpha 7
    1.  now it will save local star catalog in folder /home/Jacob975/demo/TAT_star_catalog
'''

import numpy as np
import time
import pyfits
import pywcs
from sys import argv, exit
import curvefit
import matplotlib.pyplot as plt
import os

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

# measure times
start_time = time.time()
# 0 : no print, just saving essential data
# 1 : print result
# 2 : do graph
# 3 : print debug info
VERBOSE = 0
# get all names of fits
list_name=argv[-1]
ecc = 1
list_name_list = list_name.split(".")
if list_name_list[-1] == "fits" or list_name_list[-1] == "fit":
    fits_list = [list_name]
else:
    fits_list=readfile(list_name)
if len(argv) == 3:
    ecc = argv[1]
    ecc = float(ecc)
#----------------------------------------------------------------------
# main code
if VERBOSE>0 : print "number of under processed fits:", len(fits_list)
for name in fits_list:
    if VERBOSE>0:print "--- {0} ---".format(name)
    data = pyfits.getdata(name)
    imh = pyfits.getheader(name)
    exptime = imh['EXPTIME']
    exptime = float(exptime)
    if VERBOSE>0:print exptime
    paras, cov = curvefit.hist_gaussian_fitting(name, data, shift = -7)
    data_mean = paras[0]
    data_std = paras[1]
    # peak list is a list contain elements with position tuple.
    sz = 24
    tl = 15
    peak_list = []
    while len(peak_list) > 500 or len(peak_list) < 3:
        sz += 1
        peak_list = curvefit.get_peak_filter(data, tall_limit = tl,  size = sz) 
    # star list is a list contain elements with star in this fits
    # we want to control the number of stars within 20.
    hwl = 3
    
    star_list = []
    while len(star_list) > 50 or len(star_list) < 3:
        hwl += 1
        star_list = curvefit.get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc, detailed = True)
    # check the wcs file existance, if no, the program will be end.
    try:
        hdulist = pyfits.open(name)
        wcs = pywcs.WCS(hdulist[0].header)
    except:
        print "{0} have no wcs file".format(name)
        continue
    # save star catalog
    star_list_name = name[0:-5]+"_stls.tsv"
    command = "rm {0}".format(star_list_name)
    os.system(command)
    result_file = open(star_list_name, "a")
    # write down header file
    result_file.write("# fitsname:{0}\n".format(name))
    result_file.write("# background before normalized : {0}\n".format(data_mean))
    result_file.write("# noise before normalized : {0}\n".format(data_std))
    result_file.write("# Count and magnitude data, writed below, was normalized by time = 1s\n")
    result_file.write("RAJ2000\te_RAJ2000\tDECJ2000\te_DECJ2000\tXcoord\te_Xcoord\tYcoord\te_Ycoord\tcount\te_count\tmag\te_mag\tsigma_x\te_sigma_x\tsigma_y\te_sigma_y\trotation\te_rotation\tbkg\te_bkg\n")
    result_file.write("degree\tdegree\tdegree\tdegree\tpixel\tpixel\tpixel\tpixel\tcount_per_sec\tcount_per_sec\tmag_per_sec\tmag_per_sec\tpixel\tpixel\tpixel\tpixel\tdegree\tdegree\tcount\tcount\n")
    for i in xrange(len(star_list)):
        # transform pixel to wcs
        sky = wcs.wcs_pix2sky(np.array([[star_list[i][4], star_list[i][2]]]), 1)
        sky_RA = wcs.wcs_pix2sky(np.array([[star_list[i][4] + star_list[i][5], star_list[i][2]]]), 1)
        sky_DEC = wcs.wcs_pix2sky(np.array([[star_list[i][4], star_list[i][2] + star_list[i][3]]]), 1)
        e_RA = sky_RA[0][1] - sky[0][1]
        e_DEC = sky_DEC[0][0] - sky[0][0]
        # count and magnitude must be normalized by time = 1s, in convient comparisom
        count_per_t = star_list[i][0]/exptime
        e_count_per_t = star_list[i][1]/exptime
        if VERBOSE>2:print "{0}+-{1}".format(count_per_t, e_count_per_t)
        mag = -2.5 * np.log10(count_per_t)
        mag_temp = -2.5 * np.log10(count_per_t - e_count_per_t)
        e_mag = mag_temp - mag
        if np.isnan(mag):
            continue
        temp = star_list[i]
        temp_word = "{0:.4f}\t{1:.4f}\t{2:.4f}\t{3:.4f}\t{4:.4f}\t{5:.4f}\t{6:.4f}\t{7:.4f}\t{8:.4f}\t{9:.4f}\t{10:.4f}\t{11:.4f}\t{12:.4f}\t{13:.4f}\t{14:.4f}\t{15:.4f}\t{16:.4f}\t{17:.4f}\t{18:.4f}\t{19:.4f}\n".format(sky[0][0], e_RA, sky[0][1], e_DEC, temp[2], temp[3], temp[4], temp[5], count_per_t, e_count_per_t, mag, e_mag, temp[6], temp[7], temp[8], temp[9], temp[10], temp[11], temp[12], temp[13])
        result_file.write(temp_word)
    result_file.close()    
    if VERBOSE>0:print "{0} OK".format(name)
    if VERBOSE>1:
        # draw three plot, one with point, another without
        f = plt.figure(name + ' _ini')
        plt.imshow(data, vmin = data_mean - 1 * data_std , vmax = data_mean + 1 * data_std )
        plt.colorbar()
        f.show()

        g = plt.figure(name + ' _peaks')
        plt.imshow(data, vmin = data_mean - 1 * data_std , vmax = data_mean + 1 * data_std )
        plt.colorbar()
        for pos in peak_list:
            plt.plot( pos[1], pos[0] , 'ro')
        g.show()

        h = plt.figure(name + ' _stars')
        plt.imshow(data, vmin = data_mean - 1 * data_std , vmax = data_mean + 1 * data_std )
        plt.colorbar()
        for pos in star_list:
            plt.plot( pos[2], pos[1] , 'ro')
        h.show()
        raw_input()
#-----------------------------------------------------------------------
# measuring time
elapsed_time = time.time() - start_time
if VERBOSE>0 : print "Exiting Main Thread, spending ", elapsed_time, "seconds."
