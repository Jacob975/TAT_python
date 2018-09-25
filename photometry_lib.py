#!/usr/bin/python
'''
Program:
    This is a program for save some algrithum of photometry.
Usage: 
    pick a program you like.
    shell > vim [that program]
    write down: import photometry_lib
Editor:
    Jacob975
20170216
#################################
update log
20180921 version alpha 1
    1. The code is just borned.
20180924 version alpha 2
    1. IDP is established w/o considering the error.
    2. Update the ensemble photometry to Honeycutt (1992), not finished yet.
'''
import numpy as np
import time
from scipy import optimize
from cataio_lib import get_catalog

class ensemble_photometry():
    # The demo of data structure.
    #   A target = [[ t1, flux1],
    #               [ t2, flux2]
    #               [ t3, flux3],
    #               ...
    #              ]
    #   auxilary_stars = [star1, star2, star3 ....]
    #   auxiliary_star = [[ t1, flux1],
    #                     [ t2, flux2]
    #                     [ t3, flux3],
    #                     ...
    #                    ]
    def __init__(self, target, auxiliary_stars):
        self.target = target
        self.comparison_star = comparison_star
        self.auxiliary_stars = auxiliary_stars
    def do(self):
        pass

def catalog_photometry(source):
    # If filter is A or C, skip them
    filter_ = source[18]
    print "filter = {0}".format(filter_)
    if filter_ == "A" or filter_ == "C":
        print "No corresponding band on catalog I/329"
        source[5]  = ''
        return 1, source
    # Choose the 10 brightest stars
    flux = float(source[3])
    #-------------------------------------------------
    # Find the info of the source from catalog I/329
    failure, match_star = get_catalog(source, TAT_env.URAT_1, TAT_env.index_URAT_1) 
    # Find the apparent magnitude to the found source
    failure, app_mag = get_app_mag(match_star, filter_)
    source[5] = app_mag
    return 0, source

# served as a fitting function.
def parabola(x, a, b, c):
    return a * np.power(x-b, 2) + c 

class IDP():
    # The demo of data structure.
    #   A target = [[ t1, flux1],
    #               [ t2, flux2]
    #               [ t3, flux3],
    #               ...
    #              ]
    #   comparison_star = [[ t1, flux1],
    #                      [ t2, flux2]
    #                      [ t3, flux3],
    #                      ...
    #                     ]
    #   auxilary_stars = [star1, star2, star3 ....]
    #   auxiliary_star = [[ t1, flux1],
    #                     [ t2, flux2]
    #                     [ t3, flux3],
    #                     ...
    #                    ]
    def __init__(self, target, comparison_star, auxiliary_stars):
        self.target = target
        self.comparison_star = comparison_star
        self.auxiliary_stars = auxiliary_stars
    def do(self):
        #-----------------------------------
        # Fit airmass of the comparison star
        comparison_airmass = self.fit_airmass(self.comparison_star)
        #-----------------------------------
        aux_stars_aml = []
        # All auxiliary_stars are divided by themself airmass function.
        for i in range(len(self.auxiliary_stars)):
            aux_airmass = self.fit_airmass(self.auxiliary_stars[i])
            aux_star_aml = np.transpose([self.auxiliary_stars[i,:,0], self.auxiliary_stars[i,:,1]/aux_airmass[:,1]])
            aux_stars_aml.append(aux_star_aml)
        # mean the flux of auxiliary_stars_aml
        aux_stars_aml = np.array(aux_stars_aml)
        mean_aux = np.mean(aux_stars_aml, axis = 0)
        #----------------------------------------------
        # divide the target with airmass of comparison_star and the mean of auiliary_stars_aml
        target_idp = np.transpose([self.target[:,0], np.divide(self.target[:,1], comparison_airmass[:,1])])
        target_idp = np.transpose([target_idp[:,0], np.divide(target_idp[:,1], mean_aux[:,1])])
        return target_idp, comparison_airmass, mean_aux 
    # Assume airmass is a 2d parabola curve, fit the data with this function.
    def fit_airmass(self, source):
        paras, cov = optimize.curve_fit(parabola, source[:,0], source[:,1])
        airmass = paras[0] * np.power(source[:,0] - paras[1], 2) + paras[2]
        airmass_curve = np.transpose([source[:,0], airmass])
        return airmass_curve
