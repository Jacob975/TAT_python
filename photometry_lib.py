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

# Ensemble Photometry
# Follow the steps described in Honeycutt (1992)
class EP(): 
    # The demo of data structure.
    #   A target = [[ t1, mag1, err1],
    #               [ t2, mag2, err2]
    #               [ t3, mag3, err3],
    #               ...
    #              ]
    #   comparison_stars = [star1, star2, star3 ....]
    #   comparison_star = [[ t1, mag1, err1],
    #                      [ t2, mag2, err2]
    #                      [ t3, mag3, err3],
    #                      ...
    #                     ]
    def __init__(self, target, comparison_stars):
        self.target = np.array(target)
        self.comparison_stars = np.array(comparison_stars)
    def make_airmass_model(self):
        # Load data
        all_stars = self.comparison_stars
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
        # To minimize the unknowns, let ems(1) = 0
        M_shape = (num_eps + num_stars, num_eps + num_stars)
        M = np.zeros(M_shape)
        M[num_eps:num_eps + num_stars, :num_eps] = weights_tns
        M[:num_eps, num_eps:num_eps + num_stars] = weights
        for index in xrange(num_eps + num_stars):
            if index < num_eps:
                M[index, index] = np.sum(weights[index])
            else:
                M[index, index] = np.sum(weights[:,index - num_eps]) 
        # Create a vector b for saving the observed magnitude information.
        b = np.zeros(num_eps + num_stars)
        for index in xrange(num_eps + num_stars):
            if index < num_eps:
                b[index] = np.sum(np.multiply(weights[index], signals[index]))
            else:
                b[index] = np.sum(np.multiply(weights[:,index - num_eps], signals[:, index - num_eps]))
        # Let M * a = b, find a
        # To minimize the unknowns, let ems(1) = 0
        answers = np.linalg.solve(M, b)
        ems = answers[:num_eps]
        shifted_ems = ems - ems[0]
        m0s = answers[num_eps:]
        shifted_m0s = m0s + ems[0]
        # Calculate the uncertainties of all answers.
        var_m0s = np.zeros(num_stars)
        for s in xrange(num_stars):
            top = np.sum(np.power(signals[:,s] - ems - m0s[s], 2) * weights[:, s])
            bottom = np.multiply(np.sum(weights[:,s]), float(num_eps - 1))
            var_m0s[s] = top/bottom
        var_ems = np.zeros(num_eps)
        for e in xrange(num_eps):
            top = np.sum(np.power(signals[e] - ems[e] - m0s, 2) * weights[e])
            bottom = np.multiply(np.sum(weights[e]), float(num_stars - 1))
            var_ems[e] = top/bottom
        # Upload to class
        self.ems = ems
        self.var_ems = var_ems
        self.m0s = m0s
        self.var_m0s = var_m0s
        return shifted_ems, var_ems, shifted_m0s, var_m0s
    # Do photometry on target source
    def phot(self):
        # Load data
        target = self.target
        ems = self.ems
        var_ems = self.var_ems
        utarget = unumpy.uarray(target[:,1], target[:,2])
        uems = unumpy.uarray(ems, var_ems)
        # Get the intrinsic magnitude.
        uintrinsic_target = utarget - uems
        intrinsic_signal = np.array(unumpy.nominal_values(uintrinsic_target))
        intrinsic_error  = np.array(unumpy.std_devs(uintrinsic_target))
        intrinsic_target = np.transpose([intrinsic_signal, intrinsic_error])
        return intrinsic_target 

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

# Improve Differential Photometry
# Follow the steps described in FERNANDEZ FERNANDEZ et al (2012).
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
