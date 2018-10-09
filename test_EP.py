#!/usr/bin/python
'''
Program:
    This is a test program for Ensemble Photometry. 
Usage: 
    test_EP.py
Editor:
    Jacob975
20181009
#################################
update log
'''
import numpy as np
np.set_printoptions(threshold='nan')
import time
from photometry_lib import parabola, EP 
import matplotlib.pyplot as plt
from uncertainties import unumpy, umath

# Convert flux to magnitude
def flux2mag(flux, err_flux):
    uflux = unumpy.uarray(flux, err_flux)
    umag = -2.5 * unumpy.log(uflux, 10)
    mag = unumpy.nominal_values(umag)
    err_mag = unumpy.std_devs(umag)
    return mag, err_mag

# Convert magnitude to flux
def mag2flux(mag, err_mag):
    umag = unumpy.uarray(mag, err_mag)
    uflux = 10 ** (-0.4*umag)
    flux = unumpy.nominal_values(uflux)
    err_flux = unumpy.std_devs(uflux)
    return flux, err_flux

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    t = np.arange(100)
    # Period
    T = 50
    # standard deviation
    stdev = 10
    airmass = parabola(t, -0.3, 50, 1000)
    mag_airmass = -2.5 * np.log10(airmass)
    shifted_mag_airmass = mag_airmass - mag_airmass[0]
    # Model a Target Star 
    # Sine wave (radian)
    intrinsic = np.sin(2 * np.pi * t / T) + 2
    mag_intrinsic = -2.5 * np.log10(intrinsic)
    shifted_mag_intrinsic = mag_intrinsic - mag_intrinsic[0]
    flux = airmass * intrinsic + np.random.normal(0, stdev, 100) 
    err_flux = np.sqrt(flux) 
    mag, err_mag = flux2mag(flux, err_flux)
    target = np.transpose([ t, mag, err_mag])
    # Model Comparison Stars
    comparison_stars = []
    for i in xrange(10):
        flux_tmp = airmass + np.random.normal(0, stdev, 100)
        err_flux_tmp = np.sqrt(flux_tmp)
        mag_tmp, err_mag_tmp = flux2mag(flux_tmp, err_flux_tmp)
        comparison_star = np.transpose([t, mag_tmp, err_mag_tmp])
        comparison_stars.append(comparison_star)
    comparison_stars = np.array(comparison_stars)
    student = EP(target, comparison_stars)
    ems, var_ems, m0s, var_m0s = student.make_airmass_model()
    correlated_target = student.phot()
    #----------------------------------------
    # Plot the answers
    # target
    target_plt = plt.figure("target", figsize=(8, 6), dpi=100)
    
    plt.subplot(2, 1, 1)
    plt.title('observed_target')
    plt.xlabel("time")
    plt.ylabel('mag')
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_visible(False)
    plt.errorbar(target[:,0], target[:,1], yerr = target[:,2], fmt = 'ro', label = 'observed_target')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.title('correlated_target')
    plt.ylabel('flux')
    plt.xlabel('time')
    plt.scatter(t, shifted_mag_intrinsic, label = 'intrinsic_target', alpha = 0.5)
    plt.errorbar(t, correlated_target[:,0] - correlated_target[0,0], yerr = correlated_target[:,1], fmt = 'ro', label = 'correlated_target', alpha = 0.5)
    plt.legend()
    
    # comparison_airmass
    comparison_airmass_plt = plt.figure("comparison_airmass", figsize = (8, 3), dpi = 100)
    plt.title('comparison_airmass')
    plt.ylabel('flux')
    plt.xlabel('time')
    plt.plot(t, shifted_mag_airmass, label = 'intrinsic_airmass', alpha = 0.5)
    plt.errorbar(t, ems, yerr = var_ems, fmt = 'ro', label = 'comparison_airmass', alpha = 0.5)
    plt.legend()
    
    plt.show()
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
