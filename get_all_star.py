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

20170807 version alpha 4 
    1.  add real magnitude of all band.
        del mag data is produced by $get_mag.py
        Before do $get_all_star.py, you should do $get_mag.py before.

20170808 version alpha 5
    1.  use tat_config to control path of result data instead of fix the path in the code.

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
import tat_datactrl

def get_order(tar_list, property_name_list):
    # determine the order of all property.
    ord_list = [ 0 for i in range(len(property_name_list))]
    for i in xrange(len(tar_list[0])):
        for j in xrange(len(property_name_list)):
            if tar_list[0][i] == property_name_list[j]:
                ord_list[j] = i
                break
    return ord_list

def select_by_property(tar_list, property_list, ord_list, property_name_list, VERBOSE = 0):
    # create a empty list with length of property list
    temp_list = [ [] for i in range(len(property_list)) ]
    # append original list to back
    # It wiil seem as
    # temp_list = [   [], [], [], ... ,[tar_list]  ]
    temp_list.append(tar_list)
    for i in xrange(len(ord_list)):
        if VERBOSE>0:print "current property = ",property_list[i]
        for tar in temp_list[i-1]:
            if tar[ord_list[i]] == property_list[i]:
                temp_list[i].append(tar)
    if len(temp_list[len(property_list)-1]) == 0:
        if VERBOSE>0:print "No matched data."
        return []
    return temp_list[len(property_list)-1]

def select_additional(del_mag_list):
    add_title = ""
    add_unit = ""
    band_list = ['A', 'B', 'C', 'N', 'R', 'V']
    for del_mag in del_mag_list:
        for band in band_list:
            if del_mag[7] == band:
                add_title += "{0}_mag\te_{0}_mag\t".format(band)
                add_unit += "mag_per_sec\tmag_per_sec\t"
    return add_title, add_unit

# get property of images from path
def get_img_property(image_name):
    image_name_list = image_name.split("_")
    try:
        scope_name = image_name_list[0]
        date_name = image_name_list[1]
        obj_name = image_name_list[2]
        filter_name = "{0}_{1}".format(image_name_list[3], image_name_list[4])
    except:
        print "Inproper name, get property changing ot dir"
        path = os.getcwd()
        list_path = path.split("/")
        scope_name = list_path[-5]
        date_name = list_path[-3]
        obj_name = list_path[-2]
        filter_name = list_path[-1]
    method = image_name_list[-2]
    return scope_name, date_name, obj_name, filter_name, method

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
    fits_list=tat_datactrl.readfile(list_name)

property_name_list = ["date", "scope", "band", "method", "object"]

# do what you want.
for name in fits_list:
    if VERBOSE>0:print "--- {0} ---".format(name)
    # get property of images from path
    scope_name, date_name, obj_name, band_name, method = get_img_property(name)
    property_list = [date_name, scope_name, band_name, method, obj_name]
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
    path_of_result = tat_datactrl.get_path("result")
    del_mag_list = tat_datactrl.read_tsv_file("{0}/limitation_magnitude_and_noise/delta_mag.tsv".format(path_of_result))
    ord_del_mag_list = get_order(del_mag_list, property_name_list)
    del_mag_list = select_by_property(del_mag_list, property_list, ord_del_mag_list, property_name_list)
    additional_title, additional_unit = select_additional(del_mag_list)
    result_file = open(star_list_name, "a")
    # write down header file
    result_file.write("# fitsname:{0}\n".format(name))
    result_file.write("# background before normalized : {0}\n".format(data_mean))
    result_file.write("# noise before normalized : {0}\n".format(data_std))
    result_file.write("# Count and magnitude data, writed below, was normalized by time = 1s\n")
    result_file.write("RAJ2000\te_RAJ2000\tDECJ2000\te_DECJ2000\tXcoord\te_Xcoord\tYcoord\te_Ycoord\tcount\te_count\tmag\te_mag\tsigma_x\te_sigma_x\tsigma_y\te_sigma_y\trotation\te_rotation\tbkg\te_bkg\t{0}\n".format(additional_title))
    result_file.write("degree\tdegree\tdegree\tdegree\tpixel\tpixel\tpixel\tpixel\tcount_per_sec\tcount_per_sec\tmag_per_sec\tmag_per_sec\tpixel\tpixel\tpixel\tpixel\tdegree\tdegree\tcount\tcount\t{0}\n".format(additional_unit))
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
        temp_word = "{0:.7f}\t{1:.7f}\t{2:.7f}\t{3:.7f}\t{4:.4f}\t{5:.4f}\t{6:.4f}\t{7:.4f}\t{8:.4f}\t{9:.4f}\t{10:.4f}\t{11:.4f}\t{12:.4f}\t{13:.4f}\t{14:.4f}\t{15:.4f}\t{16:.4f}\t{17:.4f}\t{18:.4f}\t{19:.4f}\t".format(sky[0][0], e_RA, sky[0][1], e_DEC, temp[2], temp[3], temp[4], temp[5], count_per_t, e_count_per_t, mag, e_mag, temp[6], temp[7], temp[8], temp[9], temp[10], temp[11], temp[12], temp[13])
        result_file.write(temp_word)
        # add the real magnitude
        for del_mag in del_mag_list:
            float_del_mag = np.float32(del_mag[0])
            e_float_del_mag = np.float32(del_mag[1])
            real_mag = mag + float_del_mag
            e_real_mag = np.sqrt(np.power(e_float_del_mag, 2) + np.power(e_mag, 2))
            result_file.write("{0:.4f}\t{1:.4f}\t".format(real_mag, e_real_mag))
            if VERBOSE>2 :print "mag = {0}, e_mag = {1}".format(real_mag, e_real_mag)
        result_file.write("\n")
    result_file.close()
    # check whether the star catalog been generated or not.
    done_star_list = glob.glob("{1}/TAT_row_star_catalog/done/{0}".format(star_list_name, path_of_result))
    if done_star_list == star_list_name:
        print "The star catalog has existed."
    else:
        command = "cp {0} {1}/TAT_row_star_catalog/{0}".format(star_list_name, path_of_result)
        os.system(command)
    # write down region file of stars in wcs and display on ds9
    if VERBOSE>1:
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
