#!/usr/bin/python
'''
Program:
This is a program to direct the position of the coordinate on image.. 
It should be only used as a library.
Classes included:
    1. pointer
        This class is used to figure out where is the point on some image.
        If there are lots of image contain this point, the code will only show the first one.
    2. ccs (celectial coordinate system)
        This is a following class of pointer, because I need some ccs calculation.

Test Usage:
1. pointer.py [RA] [DEC] [PATH]

RA: the Right accention of the point you want to take a look.
DEC: the declination of the point you want ot take a look.
PATH: Where you save these image.

editor Jacob975
20171210
#################################
update log

20171210 version alpha 1
    1. class of celectial coordinate system is partically done(init, self correction, add) 
    2. class of pointer haven't been done, this is used to find the right name of image of the star belonging to.

20171217 version alpha 2
    1. the class "pointer" is done.
    2. the class "ccs" is done.
'''
from sys import argv
import numpy as np
import pyfits
import time
import pywcs
import glob
import os
from shutil import copy2

#  this class is uesd to direct the position of the coordinate on image.
class pointer:
    # data is saved here
    # object_list means a list of object save in some folder.
    fits_name_list = None
    # sky means the point we want to take a look
    sky = None
    pix = None
    # the image where the point belonging to.
    near_image_name = None
    near_image_data = None
    near_image_header = None
    # the path we execute the code.
    init_path = None
    # the path we save the image.
    path = None
    #------------------------------------------------------------------------
    # initialize, read the coor of point and the path we save image.
    # find out which image contain the point.
    def __init__(self, RA, DEC, path):
        # save current path
        self.init_path = os.getcwd()
        # switch to the directed path
        self.path = path
        os.chdir(path)
        self.fits_name_list = glob.glob("*.fits")
        self.sky = ccs(RA, DEC)
        self.near_image_name, self.near_image_data, self.near_image_header = self.finder(self.sky)
        # check whether finder success or not
        if self.near_image_name == None:
            return
        if VERBOSE>1: self.ds9()
        return
    def finder(self, p_ccs):
        # determine the coordinate is on the image or not.
        for fits_name in self.fits_name_list:
            # the variable of saving if the point coor is valid or not.
            is_valid_x = False
            is_valid_y = False
            # read data
            hdulist = pyfits.open(fits_name)
            wcs = pywcs.WCS(hdulist[0].header)
            data = pyfits.getdata(fits_name)
            fits_header = pyfits.getheader(fits_name)
            coors = np.dstack((p_ccs.hms, p_ccs.dms))
            pix = wcs.wcs_sky2pix(coors[0], 1)
            # check whether the point is located inside the image or not.
            if 0 < pix[0][0] and pix[0][0] < len(data):
                is_valid_x = True
            if 0 < pix[0][1] and pix[0][1] < len(data):
                is_valid_y = True
            # If it is valid, copy that image to the path of the execution.
            if is_valid_y and is_valid_x:
                self.pix = pix
                if self.path != ".": copy2(fits_name, "{0}/{1}".format(self.init_path, fits_name))
                return fits_name, data, fits_header
        print "No matched image."
        return None, None, None
    def ds9(self):
        # save region
        os.chdir(self.init_path)
        region_name = "{0}_region".format(time.time())
        region_file = open(region_name, "a")
        region_file.write("{0} {1}".format(self.pix[0][0], self.pix[0][1]))
        region_file.close()
        # using ds9 to display
        cmd = "ds9 -zscale {0} -regions format xy -regions system image -regions skyformat sexagesimal -regions load {1} -zoom to fit &".format(self.near_image_name, region_name)
        os.system(cmd)
        return

# celectial coordinate system
class ccs:
    # data is saved here
    # hms: the position on RA, the unit of it is hour in this class
    # dms: the position on DEC, the unit of it is degree in this class
    hms = None
    dms = None
    def __init__(self, hms, dms):
        try:
            hms = float(hms)
        except:
            self.hms = self.read_hms(hms)
        else:
            self.hms = hms
        try:
            dms = float(dms)
        except:
            self.dms = self.read_dms(dms)
        else:
            self.dms = dms
        # check valid
        self.hms = self.check_valid_ra(self.hms)
        self.dms = self.check_valid_dec(self.dms)
        return
    # read hms from str
    def read_hms(self, coord):
        coord_list = coord.split(":")
        coord_list = map(float, coord_list)
        ans = coord_list[0]*15.0 + coord_list[1]/4.0 + coord_list[2]/240.0
        return ans
    # read dms from str
    def read_dms(self, coord):
        coord_list = coord.split(":")
        coord_list = map(float, coord_list)
        ans = coord_list[0] + coord_list[1]/60.0 + coord_list[2]/3600.0
        return ans
    
    # check the degree is valid for R.A. .
    def check_valid_ra(self, degree):
        ans = degree
        if degree >= 360.0:
            ans -= 360.0
        elif degree < 0.0:
            ans += 360.0
        return ans

    # check the degree is valid for DEC.
    def check_valid_dec(self, degree):
        ans = degree
        if degree >= 90.0:
            ans = None
        elif degree < -90.0:
            ans = None
        return ans
    # default operator: add two coordinate into one
    def __add__(self, other):
        ans_hms = self.hms + other.hms
        ans_dms = self.dms + other.dms
        return ccs(ans_hms, ans_dms)
    
    # convert dec ot dms
    def dec2dms(self, dd):
        mnt,sec = divmod(dd*3600.0 , 60)
        deg,mnt = divmod(mnt,60)
        return [deg, mnt, sec]

    # convert dec to hms
    def dec2hms(self, dd):
        mnt, sec = divmod(dd*240.0 , 60)
        hr, mnt = divmod(mnt, 60)
        return [hr, mnt, sec]
    # how to compare two coordinate.
    def __lt__(self, other):
        if self.hms < other.hms and self.dms < other.dms:
            return True
        elif self.hms > other.hms and self.dms > other.dms:
            return False
        else:
            return None
    # the format of output string.
    def __str__(self):
        dms = self.dec2dms(self.dms)
        hms = self.dec2hms(self.hms)
        line1 = "hms = {0:.2f}:{1:.2f}:{2:.2f}\n".format(hms[0], hms[1], hms[2])
        line2 = "dms = {0:.2f}:{1:.2f}:{2:.2f}".format(dms[0], dms[1], dms[2])
        return line1+line2

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 2
    # measure times
    start_time = time.time()
    '''
    # -----------------------------------
    # this part is uesd to check class ccs working.
    stu1 = ccs('0:0:1', '-1:00:01')
    stu2 = ccs('0:1:1', '0:0:1')
    print "stu1: \n{0}".format(stu1)
    print "stu2: \n{0}".format(stu2)
    print stu1 < stu2
    '''
    stu1 = pointer(argv[1], argv[2], argv[3])
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
