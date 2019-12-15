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
from uncertainties import ufloat, unumpy
from cataio_lib import get_catalog, get_app_mag
from mysqlio_lib import TAT_auth
from reduction_lib import get_rid_of_exotic
from convert_lib import mag_to_Jy, Jy_to_mag
import TAT_env

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
        self.t_series = target[:,0]
        self.comparison_stars = np.array(comparison_stars)
        self.comparison_stars[:,:,1] = np.transpose(np.transpose(   self.comparison_stars[:,:,1]) 
                                                                    - self.comparison_stars[:,0,1]
                                                                    + 1e-5)
    def make_airmass_model(self):
        #--------------------------------------------------
        # Load data
        all_stars = self.comparison_stars
        # Shape would be like this
        # "s" stands for star 
        # "e" stands for exposure
        # all_stars_t = [ [t(0,0), t(0,1), t(0,2) ... t(0,e)  ],
        #                 [t(1,0), t(1,1), t(1,2) ...         ],
        #                 [t(2,0), t(2,1), t(2,2) ...         ],
        #                     ...
        #                 [t(s,0), t(s,1), t(s,2) ... t(s,e)  ]]

        all_stars_t = all_stars[:,:,0]
        all_stars_mag = all_stars[:,:,1]
        all_stars_err = all_stars[:,:,2]
        #--------------------------------------------------
        # Get the tensor of m(e,s) "signal" and w(e,s) "weight" 
        # tns stands for transpose
        num_eps = len(all_stars[-1])
        num_stars = len(all_stars)
        # m_tns(s, e)
        signals_tns = all_stars_mag
        # w_tns(s, e)
        weights_tns = np.divide(1.0, np.power(all_stars_err, 2))
        weights_tns_filter = np.where(all_stars[:,:,1] == 0.0)
        weights_tns[weights_tns_filter] = 0.0
        # Shape would be like this
        # m(e,s)     = [ [m(0,0), m(0,1), m(0,2) ... m(0,s)  ],
        #                [m(1,0), m(1,1), m(1,2) ...         ],
        #                [m(2,0), m(2,1), m(2,2) ...         ],
        #                    ...
        #                [m(e,0), m(e,1), m(e,2) ... m(e,s)  ]]
        # m(e, s) stands for the magnitude(m) measure on the star (s) and on the exposure (e).
        signals = np.transpose(signals_tns)
        # w(e, s) stands for the weight(w) measure on the star (s) and on the exposure (e).
        weights = np.transpose(weights_tns)
        #--------------------------------------------------
        # Create a Matrix M  for saving the weight information.
        # Let M * a = b, find a
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
        # Create a vector "b" for saving the observed magnitude information.
        b = np.zeros(num_eps + num_stars)
        for index in xrange(num_eps + num_stars):
            if index < num_eps:
                b[index] = np.sum(np.multiply(weights[index], signals[index]))
            else:
                b[index] = np.sum(np.multiply(weights[:,index - num_eps], signals[:, index - num_eps]))
        #--------------------------------------------------
        # Solve a
        answers = np.linalg.solve(M, b)
        ems = answers[:num_eps]
        shifted_ems = ems - ems[0]
        m0s = answers[num_eps:]
        shifted_m0s = m0s
        #--------------------------------------------------
        # Uncertainties of all answers.
        var_m0s = np.zeros(num_stars)
        for s in xrange(num_stars):
            top = np.sum(np.power(signals[:,s] - ems - m0s[s], 2) * weights[:, s])
            bottom = np.multiply(np.sum(weights[:,s]), float(num_eps - 1.0))
            var_m0s[s] = top/bottom
        var_ems = np.zeros(num_eps)
        for e in xrange(num_eps):
            top = np.sum(np.power(signals[e] - ems[e] - m0s, 2) * weights[e])
            bottom = np.multiply(np.sum(weights[e]), float(num_stars - 1.0))
            var_ems[e] = top/bottom
        # Upload to class
        self.ems = shifted_ems
        self.var_ems = var_ems
        self.m0s = shifted_m0s
        self.var_m0s = var_m0s
        print ("ems: \n{0}".format(shifted_ems))
        print ("var_ems: \n{0}".format(var_ems))
        print ("m0s: \n{0}".format(shifted_m0s))
        print ("var_m0s: \n{0}".format(var_m0s))
        return shifted_ems, var_ems, shifted_m0s, var_m0s
    # Do photometry on target source
    def phot(self, target = []):
        if target == []:
            target = self.target
        # Load data
        t_series = np.around(np.array(target[:,0], dtype = float), decimals = 8)
        ref_t_series = np.around(np.array(self.t_series, dtype = float), decimals = 8)
        matched = np.isin(t_series, ref_t_series)
        match_timing = t_series[matched]
        # Only pick the data which match the time.
        sub_ems = self.ems[np.isin(ref_t_series, t_series)]
        sub_var_ems = self.var_ems[np.isin(ref_t_series, t_series)]
        sub_err_ems = np.sqrt(sub_var_ems)
        proper_target = target[np.isin(t_series, ref_t_series)]
        flux_target, e_flux_target  = mag_to_Jy(1.0, proper_target[:,1], proper_target[:,2])
        flux_ems, e_flux_ems        = mag_to_Jy(1.0, sub_ems, sub_err_ems)
        utarget = unumpy.uarray(flux_target, e_flux_target)
        uems    = unumpy.uarray(flux_ems, e_flux_ems)
        if len(uems) != len(utarget):
            print "Confusing source spotted."
            return True, None, None
        # Get the intrinsic magnitude "m" and error of magnitude "dm".
        #         ----------------
        # dm =  \/ a^2 + (1/SNR)^2
        #
        # where "a" is temporal error over light curve.
        #       "SNR" is the signal noise ratio derived from Poisson distribution.
        uintrinsic_flux_target   = utarget / uems
        intrinsic_flux      = np.array(unumpy.nominal_values(uintrinsic_flux_target))
        intrinsic_snr_flux  = np.array(unumpy.std_devs(uintrinsic_flux_target))
        intrinsic_a_flux    = np.std(intrinsic_flux)
        intrinsic_e_flux    = np.sqrt(intrinsic_a_flux**2 + intrinsic_snr_flux**2)
        intrinsic_mag, \
        intrinsic_e_mag     = Jy_to_mag(1.0, intrinsic_flux, intrinsic_e_flux)
        intrinsic_target    = np.transpose([match_timing, intrinsic_mag, intrinsic_e_mag])
        return False, intrinsic_target, matched 

# magnitude calibration using other catalogues.
class CATA():
    # The demo of data structure.
    #   stars are all rows in `observation_data` database.
    #   filter means the filter we take for observations.
    #   Only available for Johnson bands.
    def __init__(self, stars, filter_):
        self.stars = stars
        self.filter_ = filter_
        print "filter = {0}".format(filter_)
    # Making the model
    def make_airmass_model(self):
        print "### start to calibrate the inst mag with apparent mag in catalog I/329"
        filter_ = self.filter_
        if filter_ != 'V' and filter_ != 'B' and filter_ != 'R':
            print "This photometry doesn't this filter."
            return 1
        # Choose the 10 brightest stars
        self.index_INST_MAG = TAT_env.obs_data_titles.index('INST_MAG')
        self.index_E_INST_MAG = TAT_env.obs_data_titles.index('E_INST_MAG')
        inst_mag_array = np.array(self.stars[:,self.index_INST_MAG], dtype = float)
        mag_order_stars = self.stars[inst_mag_array.argsort()]
        print ('The number of sources: {0}'.format(len(mag_order_stars)))
        picking = np.arange(10)
        mag_order_stars = mag_order_stars[picking] 
        mag_delta_list = []
        for star in mag_order_stars: 
            #-------------------------------------------------
            # Find the info of the source from catalog I/329
            index_RA = TAT_env.obs_data_titles.index('RA')
            index_DEC = TAT_env.obs_data_titles.index('`DEC`')
            RA = float(star[index_RA])
            DEC = float(star[index_DEC])
            failure, match_stars = get_catalog(RA, DEC, TAT_env.URAT_1, TAT_env.index_URAT_1) 
            if failure:
                continue
            # Find the apparent magnitude to the found source
            failure, app_mag = get_app_mag(match_stars, filter_)
            if failure:
                continue
            inst_mag = float(star[self.index_INST_MAG])
            mag_delta = app_mag - inst_mag
            print "INST_MAG = {0}, CATA_MAG = {1}, delta = {2}".format(inst_mag, app_mag, mag_delta)
            mag_delta_list.append(mag_delta)
        # Check if the number of source is enough or not.
        if len(mag_delta_list) == 0:
            print "No enough source found in catalogue for comparison"
            return 1
        mag_delta_list = get_rid_of_exotic(mag_delta_list)
        if len(mag_delta_list) < 3:
            print "No enough source found in catalogue for comparison"
            return 1
        # remove np.nan
        mag_delta_array = np.array(mag_delta_list)
        mag_delta_array = mag_delta_array[~np.isnan(mag_delta_array)]
        # Find the median of the delta of the magnitude, and apply the result on all sources.
        self.median_mag_delta = np.median(mag_delta_array)
        return 0
    def phot(self):
        inst_mag_array = np.array(self.stars[:, self.index_INST_MAG], dtype = float)
        mag_array = inst_mag_array + self.median_mag_delta
        err_mag_array = np.array(self.stars[:, self.index_E_INST_MAG], dtype = float)
        return mag_array, err_mag_array

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
