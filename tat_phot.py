#!/usr/bin/python
'''
Program:
This is a program to code to apertrue photometry and psf photometry. 
Usage:
1. TAT_phot.py [image]
editor Jacob975
20170927
#################################
update log

20170927 version alpha 1
    apertrue part work well.

20170928 version alpha 2
    add specification of psf photometry
'''
from sys import argv
from photutils.detection import IRAFStarFinder, DAOStarFinder
from astropy.stats import gaussian_sigma_to_fwhm
from curvefit import hist_gaussian_fitting, get_peak_filter, get_star, get_star_title, get_rid_of_exotic_vector, unit_converter
from astropy.table import Table
from tat_datactrl import readfile
import numpy as np
import pyfits
import pywcs
import time

# This is used to control argus.
class argv_controller:
    fits_list = []
    def __init__(self, argu):
        self.fits_list = self.get_fitsname(argu[-1])
        return
    def get_fitsname(self, name):
        name_list = name.split(".")
        if name_list[-1] == "fits" or name_list[-1] == "fit":
            fits_list = [name]
        else:
            fits_list=tat_datactrl.readfile(name)
        return fits_list

class parameter:
    data = None
    bkg = 0.0
    std = 0.0
    sigma = 0.0
    def __init__(self, data):
        self.data = data
        self.sigma = self.get_sigma()
        paras, cov = hist_gaussian_fitting('default', data)
        self.bkg = paras[0]
        self.std = paras[1]
        return
    # This def is used to find the average sigma of a star
    def get_sigma(self):
        data = self.data
        # peak list is a list contain elements with position tuple.
        sz = 30, tl = 5
        peak_list = get_peak_filter(data, tall_limit = tl,  size = sz)
        # star list is a list contain elements with star in this fits
        hwl = 4, ecc = 1
        star_list = get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc)
        proper_star_list = self.proper_sigma(star_list, 3, 4)
        x_sigma = np.array([column[3] for column in proper_star_list])
        y_sigma = np.array([column[4] for column in proper_star_list])
        sigma = np.average([x_sigma, y_sigma], axis = None)
        return sigma
    # find coordinate and flux of a star by aperture photometry.
    def proper_sigma(self, star_list, pos_xsigma, pos_ysigma):
        # in x direction
        x_sigma = [column[pos_xsigma] for column in star_list]
        proper_x_sigma, proper_star_list = get_rid_of_exotic_vector(x_sigma, star_list, 3)
        # in y direction
        y_sigma = [column[pos_ysigma] for column in proper_star_list]
        proper_y_sigma, proper_star_list = get_rid_of_exotic_vector(y_sigma, proper_star_list, 3)
        return proper_star_list

# This class is for find the coordinate of stars and save region file by aperture photometry.
class aperphot(parameter):
    data = None
    dao_table = None
    star_table = None
    def __init__(self, paras, data):
        self.data = data
        # find peak by dao finder
        daofind = DAOStarFinder(threshold = 3.0*paras.std, fwhm=paras.sigma*gaussian_sigma_to_fwhm, roundhi=5.0, roundlo=-5.0, sharplo=0.0, sharphi=2.0, sky = paras.bkg)
        dao_table = daofind.find_stars(paras.data)
        if VERBOSE>2: print dao_table
        self.dao_table = dao_table
        # do aperture photometry
        self.star_table = self.fit()
        return
    def fit(self):
        dao_table = self.dao_table
        data = self.data
        x_list = [int(i) for i in dao_table["ycentroid"]]
        y_list = [int(i) for i in dao_table["xcentroid"]]
        peak_list = zip(x_list, y_list)
        hwl = 3
        ecc = 1
        star_list = get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc, detailed = True, VERBOSE = 1)
        # exclude some star will weird sigma
        proper_star_list = self.proper_sigma(star_list, 6, 8)
        if VERBOSE>1:
            print "number of star = {0}".format(len(star_list))
            print "number of proper star = {0}".format(len(proper_star_list))
        star_title = get_star_title(detailed = True)
        star_table = Table(rows = proper_star_list, names = star_title)
        self.star_table = star_table
        return star_table

# This is a class for save star table and star region file by psf photometry.
class psfphot(parameter):
    data = None
    psf_model = None
    dao_table = None
    star_table = None
    VERBOSE = 0
    def __init__(self, data):
        return
    def make_model(self):
        # collect normalized bright star

        # take median of all 
        # to 2-D gaussian fitting on psf_model
        psf_model = None
        return psf_model
    def fit(self, data, peak_list):
        # if the position is not in the center of pixel, do convolution.
        # subtract the star by psf_model in some amp.
        # calculate the noise of residual, find the amp of psf_model such that the noise of residual is minimum.
        star_table = None
        return star_table
    def convolution(self, psf_model, rect_func):
        # do convolution of psf_model and rect_func
        return con_psf_model

# This class is for control processing psf
class phot_control:
    data = None
    dao_table = None
    star_table = None
    fits_name = "untitle.fits"
    star_table_name = "untitle_table.fits"
    result_region_name = "untitle_region"
    dao_table_name = "untitle_dao_table.fits"
    dao_region_name = "untitle_dao_region"
    VERBOSE = 0
    def __init__(self, fits_name):
        # name setting
        self.fits_name = fits_name
        self.data = pyfits.getdata(fits_name)
        self.star_table_name = "{0}_table.fits".format(self.fits_name[0:-5])
        self.result_region_name = "{0}_region".format(self.fits_name[0:-5])
        self.dao_table_name = "{0}_dao_table.fits".format(self.fits_name[0:-5])
        self.dao_region_name = "{0}_dao_region".format(self.fits_name[0:-5])
        # test aperphot is better or psfphot?
        self.paras = parameter(self.data)
        self.star_table, self.dao_table = self.aperphot(self.paras, self.data)
        return
    # this def is for cut origin image into several piece. 
    # In order to get much more accurate psf model and fitting result.
    def puzzing(self, data):
        # some constant of puzzle
        img_x_size = len(data)
        img_y_size = len(data[0])
        piece_num = 5
        # parameters we used, include 2D list of puzz data, the position of cut in x and y axis.
        puzz_data = [[None for j in range(piece_num)] for i in range(piece_num)]
        self.x_cut = [img_x_size * i /4 for i in range(piece_num)]
        self.y_cut = [img_y_size * i /4 for i in range(piece_num)]
        for i in xrange(img_x_size-1):
            for j in xrange(img_y_size-1):
                puzz_data[i][j] = data[self.x_cut[i]:self.x_cut[i+1], self.y_cut[j]:self.y_cut[j+1]]
        return puzz_data
    # do psf fitting, powered by psfphot.
    def psfphot(self, data):
        star_table = None
        puzz_data = self.puzzing(data)
        for i in xrange(puzz_data):
            for j in xrange(puzz_data[i]):
                psffitting = psfphot(puzz_data[i][j])
                star_table = psffitting.star_table
                if star_table == None:
                    star_table = temp_star_table
                else:
                    star_table = astropy.table.join(star_table, temp_star_table)
        return star_table
    def aperphot(self, paras, data):
        aperfitting = aperphot(paras, data)
        star_table = aperfitting.star_table
        dao_table = aperfitting.dao_table
        return star_table, dao_table
    def wcs_convert(self, star_table):
        # initialized wcs
        try:
            hdulist = pyfits.open(name)
            wcs = pywcs.WCS(hdulist[0].header)
        except:
            print "{0} have no wcs file".format(name)
            return None
        # convert pixel to wcs
        # convert pixel to mag

        # setup wcs star table
        return wcs_star_table
    # save result of photometry.
    def save(self):
        star_table = self.star_table
        dao_table = self.dao_table
        # save table
        star_table.write(self.star_table_name, overwrite = True)
        # save star region
        region_file = open(self.result_region_name, "a")
        x_list = star_table["ycenter"]
        y_list = star_table["xcenter"]
        for i in xrange(len(x_list)):
            region_file.write("{0} {1}\n".format(x_list[i], y_list[i]))
        region_file.close()
        # save dao table
        dao_table.write(self.dao_table_name, overwrite = True)
        # save dao region
        region_file = open(self.dao_region_name, "a")
        x_list = dao_table["xcentroid"]
        y_list = dao_table["ycentroid"]
        for i in xrange(len(x_list)):
            region_file.write("{0} {1}\n".format(x_list[i], y_list[i]))
        region_file.close()
        return

# This is a code to control pywcs
class wcs_controller(unit_converter):
    star_table = None
    wcs_table = None
    def __init__(self, star_table):
        return
    def pix2wcs(self, star_table):
        # initialized wcs
        try:
            hdulist = pyfits.open(name)
            wcs = pywcs.WCS(hdulist[0].header)
        except:
            print "{0} have no wcs file".format(name)
            return None
        # convert pixel to wcs

        # convert pixel to mag
        count = np.array(star_table["amplitude"])
        e_count = np.array(star_table["e_amplitude"])
        mag, e_mag = self.count2mag(count, e_count)
        # setup wcs star table
        return wcs_star_table
    def save(self):
        return
#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 1
    # measure times
    start_time = time.time()
    # get property from argv
    fits_name=argv[-1]
    phot = phot_control(fits_name)
    phot.save()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
