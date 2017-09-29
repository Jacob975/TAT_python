#!/usr/bin/python
'''
Program:
This is a program to hollow images. 
Usage:
1. fit_hollow.py [edge width] [listname or fitsname]

edge width:
    The width of edge you want to leave.
fitsname or listname:
    The name of images you want to process or a list of images name you want to process.

example:
    1. fit_hollow.py some.fits          # return images in rest by 100 pixel of edge.
    2. fit_hollow.py 150 some.fits      # return images in rest by 150 pixel of edge.
editor Jacob975
20170904
#################################
update log
20170904 version alpha 1
    It runs properly
'''
from sys import argv
import numpy as np
import pyfits
import time
import tat_datactrl

# This class is used to control argv.
class argv_controller:
    # fl means file list
    fl = []
    w = 200
    def __init__(self, argu):
        if len(argu) < 2:
            print "Too less arguemnt"
            print "Usage: fit_hollow.py [edge] [fitsname or listname]"
            return
        elif len(argu) > 3:
            print "Too many argument"
            print "Usage: fit_hollow.py [fitsname or listname]"
            return
        if len(argu) == 3:
            self.w = float(argu[-2])
        list_name = argu[-1].split('.')
        if list_name[-1] == 'fits' or list_name[-1] == 'fit':
            self.fl = [argu[-1]]
        else:
            self.fl = tat_datactrl.readfile(argu[-1])
    def fits_list(self):
        return self.fl
    def width(self):
        return self.w

# This class is used to set central by np.nan
class hollower:
    name = ""
    w = 0
    # read data and graph 
    def __init__(self, name, width):
        self.name = name
        self.w = int(width)
        data = pyfits.getdata(name)
        hollow_data = self.hollow(data, self.w)
        self.save(hollow_data)
        return
    # set nan in centro
    def hollow(self, data, width):
        ans = data
        ans[width : - width , width : - width] = np.nan
        return ans
    # save data as [name]_h.fits
    def save(self, data):
        imh = pyfits.getheader(self.name)
        pyfits.writeto(self.name[0:-5]+'_h.fits', data, imh, clobber = True)
        return

# This class is used to set edge by np.nan
class shrinker:
    name = ""
    w = 0
    # read data and graph 
    def __init__(self, name, width):
        self.name = name
        self.w = int(width)
        data = pyfits.getdata(name)
        shrink_data = self.shrink(data, self.w)
        self.save(shrink_data)
        return
    # set nan in edge
    def shrink(self, data, width):
        ans = data
        ans[:width, :] = np.nan
        ans[- width:, :] = np.nan
        ans[:, : width] = np.nan
        ans[:, - width:] = np.nan
        return ans
    # save data as [name]_h.fits
    def save(self, data):
        imh = pyfits.getheader(self.name)
        pyfits.writeto(self.name[0:-5]+'_p.fits', data, imh, clobber = True)
        return

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv 
    argu = argv_controller(argv)
    for name in argu.fits_list():
        #hole = hollower(name, argu.width())
        pin = shrinker(name, argu.width())
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
