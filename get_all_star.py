#!/usr/bin/python
'''
Program:
This is a program to display and save star catalog found in fits.
The star catalog will be saved in /home/Jacob975/demo/TAT_star_catalog/

Usage:
1. get_all_star.py [fits name]
fits name
    You should put fits name here.
2. get_all_star.py [list name]
list name
    You can form a list which contain a list of fits name.
    The code will process all of them one by one.

editor Jacob975
20170719
#################################
update log

20170719 version alpha 1
    The code can run properly

20170720 version alpha 2
    It will save data in folder /home/Jacob975/demo/TAT_star_catalog/

20170727 version alpha 3 
    add error of all physical quantity.

'''
from sys import argv
from math import pow
import numpy as np
import pyfits
import pywcs
import curvefit
import time
import matplotlib.pyplot as plt
import os
import glob

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

#--------------------------------------------
# main code
VERBOSE = 1
# measure times
start_time = time.time()
# get property from argv
list_name=argv[-1]
fits_list = []

list_name_list = list_name.split(".")
if list_name_list[-1] == "fits" or list_name_list[-1] == "fit":
    fits_list = [list_name]
else:
    fits_list=readfile(list_name)

# do what you want.
for name in fits_list:
    if VERBOSE>0:print "--- {0} ---".format(name)
    data = pyfits.getdata(name)
    imh = pyfits.getheader(name)
    exptime = imh['EXPTIME']
    exptime = float(exptime)
    if VERBOSE>1:print exptime
    paras, cov = curvefit.hist_gaussian_fitting(name, data, shift = -7)
    data_mean = paras[0]
    data_std = paras[1]
    # peak list is a list contain elements with position tuple.
    # More info please read curvefit.py
    sz = 30
    tl = 3
    peak_list = curvefit.get_peak_filter(data, tall_limit = tl, size = sz)
    hwl = 4
    ecc = 1
    star_list = curvefit.get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc, detailed = True)
    # check the wcs existance, if no, the code will stop here.
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
        temp_word = "{0:.7f}\t{1:.7f}\t{2:.7f}\t{3:.7f}\t{4:.4f}\t{5:.4f}\t{6:.4f}\t{7:.4f}\t{8:.4f}\t{9:.4f}\t{10:.4f}\t{11:.4f}\t{12:.4f}\t{13:.4f}\t{14:.4f}\t{15:.4f}\t{16:.4f}\t{17:.4f}\t{18:.4f}\t{19:.4f}\n".format(sky[0][0], e_RA, sky[0][1], e_DEC, temp[2], temp[3], temp[4], temp[5], count_per_t, e_count_per_t, mag, e_mag, temp[6], temp[7], temp[8], temp[9], temp[10], temp[11], temp[12], temp[13])
        result_file.write(temp_word)
    result_file.close()
    # check whether the star catalog been generated or not.
    done_star_list = glob.glob("/home/Jacob975/demo/TAT_row_star_catalog/done/{0}".format(star_list_name))
    if done_star_list == star_list_name:
        print "The star catalog has existed."
    else:
        command = "cp {0} /home/Jacob975/demo/TAT_row_star_catalog/{0}".format(star_list_name)
        os.system(command)
    # write down region file of stars in wcs and display on ds9
    if VERBOSE>0:
        region_name = name[:-5]+".region_w"
        command = "rm {0}".format(region_name)
        os.system(command)
        result_file = open(region_name, "a")
        for i in xrange(len(star_list)):
            sky = wcs.wcs_pix2sky(np.array([[star_list[i][4], star_list[i][2]]]), 1)
            result_file.write("{0} {1}\n".format(sky[0][0], sky[0][1]))
        result_file.close()
        command = "ds9 -zscale {0} -regions format xy -regions system wcs -regions sky fk5 -regions load {1} -zoom to fit &".format(name, region_name)
        os.system(command)
    # write down region file of peaks in wcs and display
    '''
    region_name_peak = name[:-5]+".region_w_peak"
    result_file = open(region_name_peak, "a")
    for i in xrange(len(peak_list)):
        sky = wcs.wcs_pix2sky(np.array([[peak_list[i][1], peak_list[i][0]]]), 1)
        result_file.write("{0} {1}\n".format(sky[0][0], sky[0][1]))
    result_file.close()
    command = "ds9 -zscale {0} -regions format xy -regions system wcs -regions sky fk5 -regions load {1} -zoom to fit &".format(name, region_name_peak)
    os.system(command)
    '''
    if VERBOSE>0:print "{0} OK".format(name)
    if VERBOSE>2:
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

# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Program, spending ", elapsed_time, "seconds."
