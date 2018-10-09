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
from uncertainties import ufloat, unumpy

# Follow the steps described in Honeycutt (1992)
class ensemble_photometry():
    # The demo of data structure.
    #   A target = [[ t1, flux1, err1],
    #               [ t2, flux2, err2]
    #               [ t3, flux3, err3],
    #               ...
    #              ]
    #   auxilary_stars = [star1, star2, star3 ....]
    #   auxiliary_star = [[ t1, flux1, err1],
    #                     [ t2, flux2, err2]
    #                     [ t3, flux3, err3],
    #                     ...
    #                    ]
    def __init__(self, target, comparison_stars):
        self.target = target
        self.comparison_stars = comparison_stars
    def do(self):
        # Load data
        all_stars = np.append(comparison_stars, np.array([all_stars]), axis = 0)
        # Get the signal and weight 
        num_eps = len(all_stars[-1])
        num_stars = len(all_stars)
        weight_tns_shape = (num_stars, num_eps)
        weights_tns = np.zeros(weight_tns_shape)
        weights_tns = np.divide(1, np.power(all_stars[:,:,2], 2))
        weights_tns_filter = np.where(all_stars[:,:,1] == 0.0)
        # m_tns(s, e)
        signals_tns = all_stars[:, :, 1]
        # w_tns(s, e)
        weights_tns[weights_tns_filter] = 0.0
        # m(e, s)
        signals = np.transpose(signals_tns)
        # w(e, s)
        weights = np.transpose(weights_tns)
        # Create a Matrix M  for saving the weight information.
        M_shape = (num_eps + num_stars, num_eps + num_stars)
        M = np.zeros(M_shape)
        M[num_eps:num_eps + num_stars, 0:num_eps] = weights_tns
        M[0:num_eps, num_eps:num_eps + num_stars] = weights
        for index in xrange(num_eps + num_stars):
            if index < num_eps:
                M[index, index] = np.sum(weights[index])
            else:
                M[index, index] = np.sum(weights[:,index - num_eps]) 
        # Create a vector b for saving the observed magnitude information.
        for index in xrange(num_eps + num_stars):
            if index < num_eps:
                b[index] = np.sum(np.multiply(weights[index], signals[index]))
            else:
                b[index] = np.sum(np.multiply(weights[:,index - num_eps], signals[:, index - num_eps]))
        # Let M * a = b, find a
        answers = np.linalg.solve(M, b)
        ems = answers[:num_eqs]
        m0s = answers[num_eqs:]
        # Calculate the error of all answers.
        return ems, m0s

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

# The improve differential photometry with error consideration.
# Follow the steps described in FERNÁNDEZ FERNÁNDEZ et al (2012).
class IDP():
    # The demo of data structure.
    #   A target = [[ t1, flux1, stdev],
    #               [ t2, flux2, stdev]
    #               [ t3, flux3, stdev],
    #               ...
    #              ]
    #   comparison_star = [[ t1, flux1, stdev],
    #                      [ t2, flux2, stdev]
    #                      [ t3, flux3, stdev],
    #                      ...
    #                     ]
    #   auxilary_stars = [star1, star2, star3 ....]
    #   auxiliary_star = [[ t1, flux1, stdev],
    #                     [ t2, flux2, stdev]
    #                     [ t3, flux3, stdev],
    #                     ...
    #                    ]
    def __init__(self, target, comparison_star, auxiliary_stars):
        self.target = target
        self.comparison_star = comparison_star
        self.auxiliary_stars = auxiliary_stars
    def do(self):
        #-----------------------------------
        # Fit airmass of the comparison star
        comparison_airmass, comparison_aml, comparison_fluctuation = self.fit_airmass(self.comparison_star)
        #-----------------------------------
        aux_stars_aml = []
        fluctuations = []
        # All auxiliary_stars are divided by themself airmass function.
        for i in range(len(self.auxiliary_stars)):
            aux_airmass, aux_star_aml, fluctuation = self.fit_airmass(self.auxiliary_stars[i])
            aux_stars_aml.append(aux_star_aml)
            fluctuations.append(fluctuation)
        # mean the flux of auxiliary_stars_aml
        aux_stars_aml = np.array(aux_stars_aml)
        mean_aux = np.average(aux_stars_aml, axis = 0, weights = fluctuations)
        #----------------------------------------------
        # divide the target with airmass of comparison_star and the mean of auiliary_stars_aml
        u_target = unumpy.uarray(self.target[:,1], self.target[:,2])
        u_comparison_airmass = unumpy.uarray(comparison_airmass[:,1], comparison_airmass[:,2])
        target_aml = u_target/u_comparison_airmass
        u_mean_aux = unumpy.uarray(mean_aux[:,1], mean_aux[:,2])
        target_idp = target_aml/u_mean_aux
        target_idp_curve = np.transpose([self.target[:,0], unumpy.nominal_values(target_idp), unumpy.std_devs(target_idp)])
        return target_idp_curve, comparison_airmass, mean_aux 
    # Assume airmass is a 2d parabola curve, fit the data with this function.
    def fit_airmass(self, source):
        paras, cov = optimize.curve_fit(parabola, source[:,0], source[:,1])
        a = ufloat(paras[0], np.sqrt(cov[0][0]))
        b = ufloat(paras[1], np.sqrt(cov[1][1]))
        c = ufloat(paras[2], np.sqrt(cov[2][2]))
        print a, b, c
        u_source = unumpy.uarray(source[:,1], source[:,2])
        u_airmass = a * ((source[:,0] - b)**2) + c
        print u_airmass
        airmass_curve = np.transpose([source[:,0], unumpy.nominal_values(u_airmass), unumpy.std_devs(u_airmass)], )
        u_aml = u_source/u_airmass
        aml_curve = np.transpose([source[:,0], unumpy.nominal_values(u_aml), unumpy.std_devs(u_aml)])
        fluctuation = np.sum(np.power(aml_curve[:,1] - np.mean(aml_curve[:,1]),2))/(len(source) -1)
        return airmass_curve, aml_curve, fluctuation
