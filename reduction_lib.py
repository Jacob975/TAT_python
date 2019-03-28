#!/usr/bin/python
'''
Program:
    This is a library for data reduction 
Usage: 
    import reduction_lib.py
Editor:
    Jacob975
20180621
#################################
update log
20180621 version alpha 1
    1. the code looks good.
'''
from astropy.io import fits as pyfits
from fit_lib import hist_gaussian_fitting, get_peak_filter, get_star
import numpy as np
from astropy import coordinates as coord, units as u
from astropy import time as astrotime
from uncertainties import unumpy, ufloat
import os
import mysqlio_lib
#---------------------------------------------------------------------
# basic fits processing

# This is used to rotate img
# The direction needed to modified.
def rotate_images(image_list, site):
    if site == "KU":
        for name in image_list:
            imA=pyfits.getdata(name)
            imAh=pyfits.getheader(name)
            imC = np.rot90(imA, 2)
            imC = np.fliplr(imC)
            pyfits.writeto(name[0:-5]+'_r.fits', imC, imAh)
            print name[0:-5]+"_r.fits OK"
    elif site == "TF":
        for name in image_list:
            imA=pyfits.getdata(name)
            imAh=pyfits.getheader(name)
            imC = np.rot90(imA, 2)
            imC = np.fliplr(imC)
            pyfits.writeto(name[0:-5]+'_r.fits', imC, imAh)
            print name[0:-5]+"_r.fits OK"
    return

def subtract_images_subroutine(name, dark):
    imA = pyfits.getdata(name)
    imAh = pyfits.getheader(name)
    imAh['SUBBED'] = 1
    imB = np.subtract(imA, dark)
    sub_name = name.split(".")[0] 
    new_name = "{0}_subDARK.fits".format(sub_name)
    pyfits.writeto(new_name, imB, imAh, overwrite = True)
    print "{0}, OK".format(new_name)
    #---------------------------------------
    # Write to database
    cwd = os.getcwd()
    mysqlio_lib.save2sql_images(new_name, cwd)
    return new_name

# This is used to generate subDARK fits
def subtract_images(image_list, dark_name):
    dark = pyfits.getdata(dark_name)
    new_image_list = []
    for name in image_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imAh['SUBBED'] = 1
        imB = np.subtract(imA, dark)
        sub_name = name.split(".")[0] 
        new_name = "{0}_subDARK.fits".format(sub_name)
        new_image_list.append(new_name)
        pyfits.writeto(new_name, imB, imAh, overwrite = True)
        print "{0}, OK".format(new_name)
        #---------------------------------------
        # Write to database
        cwd = os.getcwd()
        mysqlio_lib.save2sql_images(new_name, cwd)
    return new_image_list

# This is used to generate divFLAT fits
def divide_images(image_list, flat_name):
    flat = pyfits.getdata(flat_name)
    new_image_list = []
    for name in image_list:
        imA = pyfits.getdata(name)
        imAh = pyfits.getheader(name)
        imAh['DIVED'] = 1
        imB = np.divide(imA, flat)
        sub_name = name.split(".")[0] 
        new_name = "{0}_divFLAT.fits".format(sub_name)
        new_image_list.append(new_name)
        pyfits.writeto(new_name, imB, imAh, overwrite = True)
        print "{0}, OK ".format(new_name)
        #---------------------------------------
        # Write to database
        cwd = os.getcwd()
        mysqlio_lib.save2sql_images(new_name, cwd)
    return new_image_list

#----------------------------------------------
# This class is for finding basic paras of image.
class image_info:
    name_image = ""
    data = None
    bkg = 0.0
    std = 0.0
    u_sigma = None
    u_sigma_x = None
    u_sigma_y = None
    exptime = 0.0
    def __init__(self, name_image):
        self.name_image = name_image
        self.data = pyfits.getdata(name_image)
        self.u_sigma_x, self.u_sigma_y = self.get_sigma()
        try:
            self.u_sigma = (self.u_sigma_x + self.u_sigma_y)/2
        except:
            self.u_sigma = ufloat(1, 1)
        paras, cov = hist_gaussian_fitting('default', self.data)
        self.amp = paras[0]
        self.bkg = paras[1]
        self.std = paras[2]
        return
    # This def is used to find the average sigma of a star
    def get_sigma(self):
        data = self.data
        # peak list is a list contain elements with position tuple.
        sz = 30
        tl = 5
        peak_list = get_peak_filter(data, tall_limit = tl, size = sz)
        # star list is a list contain elements with star in this fits
        hwl = 4
        star_array = get_star(data, peak_list, half_width_lmt = hwl)
        if len(star_array) == 0:
            print 'No star found'
            return None, None
        # sort by the amplitude
        star_array = star_array[star_array[:,0].argsort()]
        # Take the top ten brightest stars
        if len(star_array) > 10:
            star_array = star_array[-10:]
        proper_star_list = self.proper_sigma(star_array, 6, 8)
        u_sigma_x_array = unumpy.uarray(proper_star_list[:,6], proper_star_list[:,7])
        u_sigma_y_array = unumpy.uarray(proper_star_list[:,8], proper_star_list[:,9])
        u_sigma_x = u_sigma_x_array.mean()
        u_sigma_y = u_sigma_y_array.mean()
        return u_sigma_x, u_sigma_y
    # find coordinate and flux of a star by aperture photometry.
    def proper_sigma(self, star_array, ind_xsigma, ind_ysigma):
        # take out all inproper value
        # for example inf and nan
        nosigular_star_list = []
        for column in star_array:
            if np.inf in column:
                continue
            elif np.nan in column:
                continue
            nosigular_star_list.append(column)
        nosigular_star_array = np.array(nosigular_star_list)
        # in x direction
        x_sigma = nosigular_star_array[:,ind_xsigma]
        proper_x_sigma, proper_star_list = get_rid_of_exotic_vector(x_sigma, nosigular_star_array, 3)
        # in y direction
        y_sigma = nosigular_star_array[:,ind_ysigma]
        proper_y_sigma, proper_star_list = get_rid_of_exotic_vector(y_sigma, proper_star_list, 3)
        return np.array(proper_star_list)

#--------------------------------------------------------------------
# This is a func to wipe out exotic number in a list
# This one is made for matching images
def get_rid_of_exotic_severe(value_list, VERBOSE = 0):
    if VERBOSE>0:print value_list
    std = np.std(value_list)
    # resursive condition
    if std < 1 :
        return value_list
    mean = np.mean(value_list)
    # get the error of each value to the mean, than delete one with largest error.
    temp_value_list = value_list[:]
    sub_value_list = np.subtract(temp_value_list, mean)
    abs_value_list = np.absolute(sub_value_list)
    index_max = np.argmax(abs_value_list)
    temp_value_list= np.delete(temp_value_list, index_max)
    # check if the list is not exotic, if not, get in to recursive.
    value_list = get_rid_of_exotic_severe(temp_value_list)
    return value_list

# This one is made for scif calculation
def get_rid_of_exotic(value_list):
    std = np.std(value_list)
    mean = np.mean(value_list)
    # get the error of each value to the mean, than delete one with largest error.
    sub_value_list = np.subtract(value_list, mean)
    abs_value_list = np.absolute(sub_value_list)
    for i in xrange(len(abs_value_list)):
        if abs_value_list[i] >= 3 * std:
            value_list = np.delete(value_list, i)
            value_list = get_rid_of_exotic(value_list)
            return value_list
    return value_list

def get_rid_of_exotic_vector(value_list, additional, threshold = 3):
    temp_value_list = []
    temp_additional = []
    std = np.std(value_list)
    mean = np.mean(value_list)
    # get the error of each value to the mean, than delete one with largest error.
    sub_value_list = np.subtract(value_list, mean)
    abs_value_list = np.absolute(sub_value_list)
    for i in xrange(len(abs_value_list)):
        if abs_value_list[i] <= threshold * std:
            temp_value_list.append(value_list[i])
            temp_additional.append(list(additional[i]))
    if len(abs_value_list) != len(temp_value_list):
        temp_value_list, temp_additional = get_rid_of_exotic_vector(temp_value_list, temp_additional, threshold)
    return temp_value_list, temp_additional

#------------------------------------------------------------
# The functions for finding HJD, BJD, and AIRMASS

class header_editor():
    def __init__(self, header):
        try:
            self.lat = header["LATITUDE"]
        except:
            self.lat = header["LAT"]
        try:
            self.lon = header["LONGITUD"]
        except:
            self.lon = header["LONG"]
        self.site = coord.EarthLocation.from_geodetic(self.lon, self.lat)
        try:
            self.jd = float(header["JD"])
            self.times = astrotime.Time(self.jd, format='jd', scale='utc', location=self.site)
        except:
            self.date_obs = header["DATE-OBS"]
            self.time_obs = header["TIME-OBS"]
            self.times = astrotime.Time("{0}T{1}".format(self.date_obs, self.time_obs), format='isot', scale='utc', location = self.site)
            self.jd = self.times.jd
        self.ra = header["RA"]
        self.dec = header["DEC"]
        self.exptime = float(header["EXPTIME"])
        self.target = coord.SkyCoord(self.ra, self.dec, unit=(u.hourangle, u.deg), frame='icrs')
        return 
    def mjd(self):
        return self.jd - 2400000.5
    def bjd(self):
        self.ltt_bary = self.times.light_travel_time(self.target)
        bjd = self.times.utc + self.ltt_bary
        return bjd.jd
    def hjd(self):
        self.ltt_helio = self.times.light_travel_time(self.target, "heliocentric")
        hjd = self.times.utc + self.ltt_helio
        return hjd.jd
    def air_mass(self):
        mid_time = astrotime.Time(self.jd + self.exptime/86400., format='jd', scale='utc', location=self.site)
        target_altaz = self.target.transform_to(coord.AltAz(obstime = mid_time, location = self.site))
        return target_altaz.secz
