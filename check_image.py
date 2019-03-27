#!/usr/bin/python
'''
Program:
    This is a easier way to test the completeness of CCDTEMP, EXPTIME, RA, and DEC.
    It also check if CCDTEMP < -29.5 deg.
Usage: 
    check_image.py [type] [band] [exptime]
Editor:
    Jacob975
20180621
#################################
update log
20180621 alaph 6
    1. rename the code
    2. Make the code simpler
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
from fit_lib import hist_gaussian_fitting
import glob
import time
from sys import argv
from reduction_lib import header_editor
import mysqlio_lib
from joblib import Parallel, delayed

def check_header(name_image, PARAS):
    darkh=pyfits.getheader(name_image)
    # If one of header info are lost, eliminate this image.
    for para in PARAS:
        try :
            temp_a=darkh[para]
        except KeyError:
            print "{0} in {1} is wrong.".format(para, name_image)
            return 1
    # If the ccd temperature is too high, abandom this fit.
    img_temp=darkh['CCDTEMP']
    if img_temp >= -29.5:
        print "Temperature is not allow, {0} in {1}".format(img_temp, name_image)
        return 1
    return 0

# This func is used to get mean and std info of background.
def bkg_info(name_image):
    # save the bkg and stdev of each img.
    try:
        data = pyfits.getdata(name_image)
        params, cov = hist_gaussian_fitting("default", data, shift = -7)
    except:
        print "background not found in {0}".format(name_image)
        return 1, 0, 0
    mean_bkg = params[0]
    std_bkg = params[1]
    return 0, mean_bkg, std_bkg

def add_jd_airmass_info(name_image):
    data = pyfits.getdata(name_image)
    header = pyfits.getheader(name_image)
    try:
        stu = header_editor(header)
        jd = stu.jd
        mjd = stu.mjd()
        hjd = stu.hjd()
        bjd = stu.bjd()
        air_mass = stu.air_mass().value
    except:
        print "Fail to update header with HJD, BJD, AIRMASS."
        return 1
    header["JD"] = jd
    header["MJD"] = mjd
    header["HJD"] = (hjd, "Heliocentric Julian Date")
    header["BJD"] = (bjd, "Barycentric, Julian Date")
    header["AIRMASS"] = (air_mass, "Air mass when a half of exposure.")
    pyfits.writeto(name_image, data, header, overwrite = True)
    return 0

#--------------------------------------------
# main code
if __name__ == "__main__":
    # measure times
    start_time = time.time()
    #----------------------------------------
    # Load Arguments
    if len(argv) != 4:
        print "Error! Wrong arguments"
        print "Usage: check_image.py [type] [band] [exptime]"
        print "Available type: data, dark, flat"
        print "Available bands: A, B, C, N, R, V"
        exit()
    print ("### check image ###")
    # make a list with names of images in this directory
    type_ = argv[1]
    band = argv[2]
    exptime = argv[3]
    print "type: {0}, band: {1}, exptime: {2}".format(type_, band, exptime)
    #---------------------------------------
    # Initialize
    image_list = []
    if type_ == 'data':
        image_list = glob.glob('{0}*.fit'.format(band))
        PARAS=['CCDTEMP','EXPTIME','RA','DEC']
    elif type_ == 'dark':
        image_list = glob.glob('dark*{0}.fit'.format(exptime))
        PARAS=['CCDTEMP','EXPTIME']
    elif type_ == 'flat':
        image_list = glob.glob('{0}flat*{1}.fit'.format(band, exptime))
        PARAS=['CCDTEMP','EXPTIME']
    # check the valid of image_list
    if len(image_list) == 0:
        print "No image found"
        exit()
    # There are the parameters of header infos
    mean_bkgs = []
    std_bkgs = []
    bad_headers = []
    bad_bkgs = []
    print "--- data reduction ---"
    #---------------------------------------
    # Header and check
    # check headers of images, then load mean and std of background.
    for name_image in image_list:
        failure = check_header(name_image, PARAS)
        if failure:
            bad_headers.append(1)
            command = "mv {0} X_{0}_X".format(name_image)
            os.system(command)
            mean_bkgs.append(0)
            std_bkgs.append(0)
            continue
        bad_headers.append(0)
        # If image type is data, add more infos into header
        if type_ == 'data':
            add_jd_airmass_info(name_image)
        # read bkg info of image
        failure, mean_bkg, std_bkg = bkg_info(name_image)
        if failure:
            mean_bkgs.append(0)
            std_bkgs.append(0)
            continue
        mean_bkgs.append(mean_bkg)
        std_bkgs.append(std_bkg)
        print "{0}, checked".format(name_image)
    mean_bkgs = np.array(mean_bkgs)
    std_bkgs = np.array(std_bkgs)
    #----------------------------------------
    # Image quality check
    # mean of bkgs should be consistent
    bad_bkgs = np.zeros(len(mean_bkgs), dtype = int)
    interset_of_bad = np.zeros(len(mean_bkgs), dtype = int)
    if type_ != 'flat':
        no_loss_in_mean_bkgs = np.where(mean_bkgs != 0)
        median_mean_bkgs = np.median(mean_bkgs[no_loss_in_mean_bkgs])
        print "median_mean_bkgs = {0}".format(median_mean_bkgs)
        no_loss_in_std_bkgs = np.where(std_bkgs != 0)
        median_std_bkgs = np.median(std_bkgs[no_loss_in_std_bkgs])
        print "median_std_bkgs = {0}".format(median_std_bkgs)
        index_of_bad_bkgs = np.where(np.absolute(mean_bkgs - median_mean_bkgs) > 5 * median_std_bkgs)
        bad_bkgs[index_of_bad_bkgs] = 1
        print "bad_bkgs:\n{0}".format(bad_bkgs)
        bad_headers = np.array(bad_headers)
        print "bad_headers:\n{0}".format(bad_headers)
        index_of_interset_of_bad = np.where((bad_headers == 1) & (bad_bkgs == 1))
        interset_of_bad[index_of_interset_of_bad] = 1
        print "interset_of_bad:\n{0}".format(interset_of_bad)
        for i in xrange(len(mean_bkgs)):
            if bad_bkgs[i] == 1 and bad_headers[i] == 0:
                command = "mv {0} X_{0}_X".format(image_list[i])
                os.system(command)
    #-----------------------------------------
    print "--- Check finished! ---"
    print "Number of total image: {0}".format(len(image_list))
    print "Number of success: {0}".format(len(image_list) - np.sum(bad_headers, dtype = int) - np.sum(bad_bkgs, dtype = int) + np.sum(interset_of_bad, dtype = int)) 
    print "Number of broken header: {0}".format(np.sum(bad_headers, dtype = int))
    if type_ != 'flat':
        print "Number of inconsistent background: {0}".format(np.sum(bad_bkgs, dtype = int))
    #---------------------------------------
    # Write to database
    cwd = os.getcwd()
    Parallel(   n_jobs=10)(\
                delayed(mysqlio_lib.save2sql_images)(name, cwd) for name in image_list)
    #---------------------------------------
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
