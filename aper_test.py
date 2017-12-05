#!/usr/bin/python
'''
Program:
This is a program to do aperture photometry
Usage:
1. aper_test.py [fits_name]
editor Jacob975
20171130
#################################
update log

20171130 version alpha 1
    1. the code works, but all parameters need to be modified inside editor.

20171206 version alpha 2
    1. add a new parameters, name, used to control the name of plot.
    2. I using get_rid_of_exotic to wipe out bright star affect on bkg region.
'''
from sys import argv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import pyfits
import time
import curvefit

class argv_controller:
    def __init__(self):
        return

class aper_phot:
    # input variable
    data = None
    # output variable
    flux = None
    e_flux = None
    bkg = None
    # parameters
    region_radius = None
    inner_bkg_radius = None
    outer_bkg_radius = None
    shape = None
    shape_options = ["circle", "rect"]
    name = 0
    VERBOSE = 0
    # the main sequense of aperture photometry process
    def __init__(self, data, region_radius = 12, inner_bkg_radius = 16, outer_bkg_radius = 18, shape = "rect", name = 0, VERBOSE = 0):
        self.data = data
        self.region_radius = region_radius
        self.inner_bkg_radius = inner_bkg_radius
        self.outer_bkg_radius = outer_bkg_radius
        self.name = name
        self.VERBOSE = VERBOSE
        if shape == "rect":
            self.flux, self.e_flux, self.bkg = self.get_flux_rect(data)
            if self.VERBOSE>1:
                self.plot_rect()
        if shape == "circle":
            self.flux, self.e_flux, self.bkg = self.get_flux_circle(data)
            if self.VERBOSE>1:
                self.plot_circle()
        return
    # the part of getting flux of stellar matters in region with rect aperture.
    def get_flux_rect(self, data):
        #--------------------------
        # prepare some parameters
        #--------------------------
        # mp means middle point
        mp = len(data)/2
        # rd means region radius
        rd = self.region_radius
        ibd = self.inner_bkg_radius
        obd = self.outer_bkg_radius
        if self.VERBOSE>2:print "mp: {0}, rd: {1}, ibd: {2}, obd: {3}".format(mp, rd, ibd, obd)
        #--------------------------------
        # main process of this code
        #-------------------------------
        gross_flux = np.array(data[mp-rd:mp+rd , mp-rd:mp+rd])
        gross = np.array(data[mp-obd:mp+obd, mp-obd:mp+obd])
        # gmp is middle point of gross
        gmp = len(gross)/2
        # the the point out of range of background as np.nan
        gross[gmp-ibd:gmp+ibd, gmp-ibd:gmp+ibd] = np.nan
        in_region = np.invert(np.isnan(gross))
        # find bkg and e_bkg
        bkg_array = gross[in_region]
        bkg_array = curvefit.get_rid_of_exotic(bkg_array)
        bkg = np.mean(bkg_array)
        e_flux = np.std(bkg_array)
        gross_flux = gross_flux - bkg
        flux = np.sum(gross_flux)
        if self.VERBOSE>2:print "total flux = {0:.2f}, bkg = {1:.2f}+-{2:.2f}".format(flux, bkg, e_flux)
        return flux, e_flux, bkg
    def plot_rect(self):
        #--------------------------
        # prepare some parameters
        #--------------------------
        # mp means middle point
        mp = len(self.data)/2
        # rd means region radius
        rd = self.region_radius
        ibd = self.inner_bkg_radius
        obd = self.outer_bkg_radius
        #--------------------
        # start to plot
        #--------------------
        result_plt = plt.figure("aper phot {0}".format(self.name))
        plt.imshow(self.data, vmin = self.bkg - 3*self.e_flux, vmax = self.bkg + 3*self.e_flux)
        plt.colorbar()
        axe = plt.gca()
        # obr means outer bkg range
        obr = Rectangle((mp-obd, mp-obd), 2*obd, 2*obd, linewidth=1, edgecolor='r',facecolor='none')
        # ibr means inner bkg range
        ibr = Rectangle((mp-ibd, mp-ibd), 2*ibd, 2*ibd, linewidth=1, edgecolor='g',facecolor='none')
        # rr means radius region, where I am interested in.
        rr = Rectangle((mp-rd, mp-rd), 2*rd, 2*rd, linewidth=1, edgecolor='b',facecolor='none')
        axe.add_patch(obr)
        axe.add_patch(ibr)
        axe.add_patch(rr)
        result_plt.show()
        result_plt.savefig("rect_aper_{0}.png".format(self.name))
        return
    # the part of getting flux of stellar matters in region with circle aperture.
    def get_flux_circle(self, data):
        #--------------------------
        # prepare some parameters
        #--------------------------
        # mp means middle point
        mp = len(data)/2
        # rd means region radius
        rd = self.region_radius
        ibd = self.inner_bkg_radius
        obd = self.outer_bkg_radius
        if self.VERBOSE>2:print "mp: {0}, rd: {1}, ibd: {2}, obd: {3}".format(mp, rd, ibd, obd)
        #--------------------------------
        # main process of this code
        #-------------------------------
        x, y = np.ogrid[-mp:mp,-mp:mp]
        gross_flux_mask = np.power(x, 2) + np.power(y, 2) <= np.power(rd, 2)
        gross_o_mask = np.power(x, 2) + np.power(y, 2) <= np.power(obd, 2)
        gross_i_mask = np.power(x, 2) + np.power(y, 2) <= np.power(ibd, 2)
        gross_hollow_mask = gross_o_mask - gross_i_mask
        bkg_array = data[gross_hollow_mask]
        bkg_array = curvefit.get_rid_of_exotic(bkg_array)
        bkg = np.mean(bkg_array)
        e_flux = np.std(bkg_array)
        flux_matrix = np.array(data - bkg)
        flux = np.sum(flux_matrix[gross_flux_mask])
        if self.VERBOSE>2:print "total flux = {0:.2f}, bkg = {1:.2f}+-{2:.2f}".format(flux, bkg, e_flux)
        return flux, e_flux, bkg
    def plot_circle(self):
        #--------------------------
        # prepare some parameters
        #--------------------------
        # mp means middle point
        mp = len(self.data)/2
        # rd means region radius
        rd = self.region_radius
        ibd = self.inner_bkg_radius
        obd = self.outer_bkg_radius
        #--------------------
        # start to plot
        #--------------------
        result_plt = plt.figure("aper phot {0}".format(self.name))
        plt.imshow(self.data, vmin = self.bkg - 3*self.e_flux, vmax = self.bkg + 3*self.e_flux)
        plt.colorbar()
        axe = plt.gca()
        # obc means outer bkg circle
        obc = Circle((mp, mp), obd, linewidth=1, edgecolor='r',facecolor='none')
        # ibc means inner bkg circle
        ibc = Circle((mp, mp), ibd, linewidth=1, edgecolor='g',facecolor='none')
        # rc means radius circle, where I am interested in.
        rc = Circle((mp, mp), rd, linewidth=1, edgecolor='b',facecolor='none')
        axe.add_patch(obc)
        axe.add_patch(ibc)
        axe.add_patch(rc)
        result_plt.show()
        result_plt.savefig("circ_aper_{0}.png".format(self.name))
        return
#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv
    fits_name=argv[-1]
    imA = pyfits.getdata(fits_name)
    student = aper_phot(imA,shape = "circle", VERBOSE = 3)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
