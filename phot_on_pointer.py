#!/usr/bin/python
'''
Program:
This is a program to phot a point on different images with the same wcs.
Usage:
1. phot_on_pointer.py [RA] [DEC] [rr] [ibr] [obr] [opt]

RA:     right accention of that point
DEC:    declination of that point
rr:     radius region of the aperphot
ibr:    inner boundary radius of the aperphot
obr:    outer boundary radius of the aperphot

editor Jacob975
20171225
#################################
update log

20171225 version alpha 1
    1. the concept of do phot at certain point is revealing.

20171226 version alpha 2
    1. the code works well!
'''
from sys import argv
from tat_phot import parameter
from ptr_lib import ccs
from astropy.table import Table, Column
import aper_lib
import numpy as np
import pyfits
import pywcs
import time
import glob
import datetime

# This class is used to arragne argument.
class argv_controller:
    # the data of this class is saved here
    # opt_list means all possible option you can use
    # -a means the program will resolve all image to construct the catalog
    # -s means the program will only resolve the first image be found. 
    opt_list = ['-a', '-s']
    # opt means the option you choose
    # default by '-u'
    opt = '-a'
    # the position you want to do aper phot.
    p_ccs = None
    # the range you want to do aper phot
    rr = 0.0
    ibr = 0.0
    obr = 0.0
    # the name of the code
    code_name = None
    # the starting time
    START_TIME = None
    # the name of log
    # all thing the code do will be save in log file
    LOGNAME = None
    # how load the code be
    VERBOSE = 2
    # ---------------------------------------------
    # initialized the class
    def __init__(self, argu_list, VERBOSE = 2):
        # set the VERBOSE
        self.VERBOSE = VERBOSE
        # set the initial time
        self.START_TIME = time.time()
        RA = 0.0
        DEC = 0.0
        # arrange argument
        for argu in argu_list:
            # skip the first argu, which is usually the name of the code.
            if argu_list.index(argu) == 0:
                self.code_name = argu
                continue
            # skip the second argu, which should be RA.
            elif argu_list.index(argu) == 1:
                RA = argu
                continue
            # skip the third argu, which should be DEC.
            elif argu_list.index(argu) == 2:
                DEC = argu
                continue
            # skip the forth to sixth, they are the boundary of aperphot.
            elif argu_list.index(argu) == 3:
                self.rr = argu
                continue
            # inner boundary radius
            elif argu_list.index(argu) == 4:
                self.ibr = argu
                continue
            # outer boundary radius
            elif argu_list.index(argu) == 5:
                self.obr = argu
                continue
            # the the option
            for opt in self.opt_list:
                if opt == argu:
                    self.opt = argu
        # set the point
        self.p_ccs = ccs(RA, DEC)
        # set the log name
        self.LOGNAME = "{0}_phot_on_pointer.log".format(self.START_TIME)
        if VERBOSE>1: print "the log will be saved here: {0}".format(self.LOGNAME)
        # write log 
        self.savelog()
        return
    def savelog(self):
        log_file = open(self.LOGNAME, "a+")
        log_file.write("the option: {0}\n".format(self.opt))
        log_file.close()
        return

class cursor:
    # the data of this class is saved here
    # opt_list means all possible option you can use
    # -a means the program will resolve all image to construct the catalog
    # -s means the program will only resolve the first image be found. 
    opt_list = ['-a', '-s']
    # the title and unit of the table
    titles = np.array(["RAJ2000", "DECJ2000", "xcenter", "ycenter", "flux", "bkg", "e_bkg", "date", "band", "scope", "method", "exptime"])
    units = np.array(["hhmmss", "ddmmss", "pix", "pix", "count", "count", "count", "yyyymmdd", "", "", "", "sec"])
    # opt means the option you choose
    # default by '-u'
    opt = '-a'
    # the position you want to do aper phot.
    p_ccs = None
    # the range you want to do aper phot
    rr = 0.0
    ibr = 0.0
    obr = 0.0
    # the name of the code
    code_name = None
    # the starting time
    START_TIME = None
    # the name of log
    # all thing the code do will be save in log file
    LOGNAME = None
    # the list of image name waiting for processing.
    fits_name_list = None
    # where you save the result of aperphot
    result_table = None
    result_table_name = None
    # how load the code be
    VERBOSE = 2
    def __init__(self, arg_ctrl, VERBOSE = 2):
        # pass constant
        self.VERBOSE = VERBOSE
        self.opt = arg_ctrl.opt
        self.START_TIME = arg_ctrl.START_TIME
        self.LOGNAME = arg_ctrl.LOGNAME
        self.p_ccs = arg_ctrl.p_ccs
        self.rr = float(arg_ctrl.rr)
        self.ibr = float(arg_ctrl.ibr)
        self.obr = float(arg_ctrl.obr)
        self.fits_name_list = glob.glob("*.fits")
        self.result_table_name = "{0}_phot_on_pointer.fits".format(self.START_TIME)
        # If you choose to process all images
        if self.opt == '-a':
            for name in self.fits_name_list:
                if VERBOSE>2: print self.result_table
                star_table = self.phot(name)
                if star_table == None:
                    continue
                elif self.result_table == None:
                    self.result_table = star_table
                else:
                    self.result_table.add_row(star_table[0])
        # If you choose to process the first image contain the point
        elif self.opt == '-s':
            for name in self.fits_name_list:
                star_table = self.phot(name)
                if star_row == None:
                    continue
                else:
                    self.result_table = Table(star_table)
                    break
        self.savelog()
    # given an image, find the result of aperphot of the point on it.
    # if the point is not on the image, return None.
    def phot(self, fits_name):
        # read wcs of image, convert wcs to pix on the image
        pix = self.sky2pix(self.p_ccs, fits_name)
        # check the point is on this image
        data = pyfits.getdata(fits_name)
        is_valid_x = False
        is_valid_y = False
        # check whether the point is located inside the image or not.
        if 0 < pix[0][0] and pix[0][0] < len(data):
            is_valid_x = True
        if 0 < pix[0][1] and pix[0][1] < len(data):
            is_valid_y = True
        print pix[0][0], pix[0][1]
        # If it is valid, compute the result
        if is_valid_y and is_valid_x:
            # cut the region we are interested in.
            x = int(pix[0][0])
            y = int(pix[0][1])
            obr = int(self.obr)
            star_data = data[x-obr : x+obr , y-obr : y+obr]
            wk = aper_lib.aper_phot(star_data, self.rr, self.ibr, self.obr, shape = "circle", name = fits_name, VERBOSE = 0)
            # read info from image header
            wk2 = parameter_lite(fits_name)
            obj_list = [[self.p_ccs.hms, self.p_ccs.dms, x, y, wk.flux, wk.bkg, wk.e_bkg, wk2.date, wk2.band, wk2.scope, wk2.method, wk2.exptime]]
            print len(obj_list)
            print len(self.titles)
            print len(self.units)
            # initialize the table
            star_table = Table(rows = obj_list, names = self.titles)
            # setting unit
            for i in xrange(len(self.units)):
                star_table[self.titles[i]].unit = self.units[i]
            return star_table
        else: 
            return None
    # the def is used to convert sky to pix position
    def sky2pix(self, sky, fits_name):
        hdulist = pyfits.open(fits_name)
        wcs = pywcs.WCS(hdulist[0].header)
        coors = np.dstack((sky.hms, sky.dms))
        pix = wcs.wcs_sky2pix(coors[0], 1)
        return pix
    def savedata(self):
        # save the table 
        self.result_table.write(self.result_table_name, overwrite = True)
        # save the plot of flux versus date
        return
    def savelog(self):
        log_file = open(self.LOGNAME, "a+")
        time_stamp = datetime.datetime.fromtimestamp(self.START_TIME).strftime('%Y-%m-%d %H:%M:%S')
        log_file.write("# date: {0}\n".format(time_stamp))
        log_file.write("# program: {0}\n".format(self.code_name))
        log_file.write("# Processed files:\n")
        for name in self.fits_name_list:
            log_file.write("{0}\n".format(name))
        log_file.close()
        return

class parameter_lite(parameter):
    def __init__(self, fits_name):
        self.observator_property(fits_name)
        return
#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # a brave student is ready to try something new!!
    stu = argv_controller(argv)
    stu2 = cursor(stu)
    stu2.savedata()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
