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

    20170822 version alpha 8
    1.  The code has been classified.
    2.  file format of result data is changed from tsv to fits.
'''

import numpy as np                  # precise and fast math module
import time                         # used to control time spending
import pyfits                       # fits I/O module
import pywcs                        # read wcs from fits image
from sys import argv, exit          # read argument from outside
from astropy.table import Table     # an table I/O module
from astropy.io import fits         # an file I/O module
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
#-----------------------------------------------------
# This class is for control argument from outside.
class argv_ctrl:
    argument = []
    fl = []
    e = 1.0
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        if len(argument) == 1:
            print "Usage: get_info.py [eccentricity] [list name]"
            return
        elif len(argument) == 2:
            self.listup(argument[-1])
            return
        elif len(argument) == 3:
            self.listup(argument[-1])
            self.e = float(argument[-2])
            return
        else:
            print "Too many argument"
            print "Usage: get_info.py [eccentricity] [list name]"
            return
    # check whether the file is a fits or a list
    # If it is a list, the code will read all name in the list
    # If it is a fits, the code will setup a list containing only that name of fits.
    def listup(self, list_name):
        list_name_list = list_name.split(".")
        if list_name_list[-1] == "fits" or list_name_list[-1] == "fit":
            self.fl = [list_name]
        else:
            self.fl = readfile(list_name)
    # for return value
    def fits_list(self):
        return self.fl
    def ecc(self):
        return self.e
#---------------------------------------------------------
# This code for process image
class main_process:
    fitsname = ""
    data = np.array([])
    std = 0.0
    mean = 0.0
    star_table = None
    peak_table = None
    result_table = None
    def __init__(self, name, ecc):
        self.fitsname = name
        self.ecc = ecc
        if VERBOSE>0:print "--- {0} ---".format(name)
        # check the wcs file existance, if no, the program will be end.
        try:
            hdulist = pyfits.open(name)
            wcs = pywcs.WCS(hdulist[0].header)
        except:
            print "{0} have no wcs file".format(name)
            return 
        # record info of stars in this image in a table
        star_table, peak_table, result_table = self.data_process(name)
        self.star_table = star_table
        self.peak_table = peak_table
        self.result_table = result_table
        # save the result table into fits file
        self.save()
        # plot the result of peak list and star list.
        if VERBOSE>1: self.plot()
        return
    def data_process(self, name):
        data = pyfits.getdata(name)
        self.data = data
        imh = pyfits.getheader(name)
        exptime = imh['EXPTIME']
        exptime = float(exptime)
        paras, cov = curvefit.hist_gaussian_fitting(name, data, shift = -7)
        self.mean = paras[0]
        self.std = paras[1]
        # peak list is a list contain elements with position tuple.
        # we want to control the number of peaks within 500
        sz = 24
        tl = 15
        peak_list = []
        while len(peak_list) > 500 or len(peak_list) < 3:
            sz += 1
            peak_list = curvefit.get_peak_filter(data, tall_limit = tl,  size = sz)
        peak_title = curvefit.get_peak_title()
        peak_table = Table(rows = peak_list, names = peak_title)
        # star list is a list contain elements with star in this fits
        # we want to control the number of stars within 20.
        hwl = 3
        star_list = []
        while len(star_list) > 50 or len(star_list) < 3:
            hwl += 1
            star_list = curvefit.get_star(data, peak_list, half_width_lmt = hwl, eccentricity = self.ecc, detailed = True)
            if VERBOSE>1: print "number of star: {0}".format(len(star_list))
        star_title = curvefit.get_star_title(detailed = True)
        star_table = Table(star_list, names = star_title)
        result_list = []
        hdulist = pyfits.open(name)
        wcs = pywcs.WCS(hdulist[0].header)
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
            tmp = np.array([sky[0][0], e_RA, sky[0][1], e_DEC, temp[2], temp[3], temp[4], temp[5], count_per_t, e_count_per_t, mag, e_mag, temp[6], temp[7], temp[8], temp[9], temp[10], temp[11], temp[12], temp[13]])
            result_list.append(tmp)
        result_title = np.array(["RAJ2000", "e_RAJ2000", "DECJ2000", "e_DECJ2000", "Xcoord", "e_Xcoord", "Ycoord", "e_Ycoord", "count", "e_count", "mag", "e_mag", "sigma_x", "e_sigma_x", "sigma_y", "e_sigma_y", "rotation", "e_rotation", "bkg", "e_bkg"])
        result_unit = np.array(["degree", "degree", "degree", "degree", "pixel", "pixel", "pixel", "pixel", "count_per_sec", "count_per_sec", "mag_per_sec", "mag_per_sec", "pixel", "pixel", "pixel", "pixel", "degree", "degree", "count", "count"])
        # set up result table
        result_table = Table(rows = result_list, names = result_title)
        # set up unit of result table
        for i in xrange(len(result_unit)):
            result_table[result_title[i]].unit = result_unit[i]
        return star_table, peak_table, result_table
    def plot(self):
        # draw three plot, one with point, another without
        f = plt.figure(self.fitsname + ' _ini')
        plt.imshow(self.data, vmin = self.mean - 1 * self.std , vmax = self.mean + 1 * self.std )
        plt.colorbar()
        f.show()

        g = plt.figure(self.fitsname + ' _peaks')
        plt.imshow(self.data, vmin = self.mean - 1 * self.std , vmax = self.mean + 1 * self.std )
        plt.colorbar()
        for pos in self.peak_table:
            plt.plot( pos['ycenter'], pos['xcenter'] , 'ro')
        g.show()

        h = plt.figure(self.fitsname + ' _stars')
        plt.imshow(self.data, vmin = self.mean - 1 * self.std , vmax = self.mean + 1 * self.std )
        plt.colorbar()
        for pos in self.star_table:
            plt.plot( pos["ycenter"], pos["xcenter"] , 'ro')
        h.show()
        raw_input()
        return
    def save(self):
        # save star catalog
        star_list_name = self.fitsname[0:-5]+"_stls.fits"
        self.result_table.write(star_list_name, overwrite = True)
        # write down header file
        comment_list = ["fitsname is {0}".format(self.fitsname), "background before normalized : {0}".format(self.mean), "noise before normalized : {0}".format(self.std), "Count and magnitude data, writed below, was normalized by time = 1s"]
        hdulist = fits.open(star_list_name, mode = 'update')
        prihdr = hdulist[0].header
        for i in xrange(len(comment_list)):
            prihdr['COMMENT'] = comment_list[i]
        hdulist.flush()
        hdulist.close()
        if VERBOSE>0:print "{0} OK".format(self.fitsname)
        return

#----------------------------------------------------------------------
# main code
if __name__ == "__main__":
    # measure times
    start_time = time.time()
    # 0 : no print, just saving essential data
    # 1 : print result
    # 2 : do graph
    # 3 : print debug info
    VERBOSE = 2
    # get argument form argv by class: argv_ctrl
    argument = argv_ctrl(argv)
    # read a list of fits name
    fits_list = argument.fits_list()
    ecc = argument.ecc()
    if VERBOSE>0 : print "number of under processed fits:", len(fits_list)
    # find star list of all fits and save the result .
    for name in fits_list:
        execution = main_process(name, ecc)
#-----------------------------------------------------------------------
# measuring time
    elapsed_time = time.time() - start_time
    if VERBOSE>0 : print "Exiting Main Thread, spending ", elapsed_time, "seconds."
