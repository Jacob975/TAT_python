#!/usr/bin/python
'''
Program:
    This is a test program for Improved Differential Photometry(IDP) 
Usage: 
    test_IDP.py
Editor:
    Jacob975
20189024
#################################
update log
'''
import numpy as np
import time
from photometry_lib import parabola, IDP
import matplotlib.pyplot as plt

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
    # sine wave (radian)
    intrinsic = np.sin(2 * np.pi * t / T) + 2
    flux = airmass * intrinsic + np.random.normal(0, stdev, 100)
    target = np.transpose([ t, flux, np.sqrt(flux)])
    
    flux_comparison = airmass + np.random.normal(0, stdev, 100)
    comparison_star = np.transpose([t, flux_comparison, np.sqrt(flux_comparison)])
    
    flux_1 = airmass + np.random.normal(0, stdev, 100)
    auxiliary_star1 = np.transpose([t, flux_1, np.sqrt(flux_1)])
    
    flux_2 = airmass + np.random.normal(0, stdev, 100)
    auxiliary_star2 = np.transpose([t, flux_2, np.sqrt(flux_2)])
    
    flux_3 = airmass + np.random.normal(0, stdev, 100)
    auxiliary_star3 = np.transpose([t, flux_3, np.sqrt(flux_3)])
    
    auxiliary_stars = np.array([auxiliary_star1, auxiliary_star2, auxiliary_star3])
    student = IDP(target, comparison_star, auxiliary_stars)
    correlated_target, comparison_airmass, mean_aml = student.do() 
    #----------------------------------------
    # Plot the answers
    # target
    target_plt = plt.figure("target", figsize=(8, 6), dpi=100)
    
    plt.subplot(2, 1, 1)
    plt.title('observed_target')
    plt.ylabel('flux')
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_visible(False)
    plt.errorbar(target[:,0], target[:,1], yerr = target[:,2], fmt = 'ro', label = 'observed_target')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.title('correlated_target')
    plt.ylabel('flux')
    plt.xlabel('time')
    plt.scatter(t, intrinsic, label = 'intrinsic_target', alpha = 0.5)
    plt.errorbar(correlated_target[:,0], correlated_target[:,1], yerr = correlated_target[:,2], fmt = 'ro', label = 'correlated_target', alpha = 0.5)
    plt.legend()
    
    # comparison_airmass
    comparison_airmass_plt = plt.figure("comparison_airmass", figsize = (8, 3), dpi = 100)
    plt.title('comparison_airmass')
    plt.ylabel('flux')
    plt.xlabel('time')
    plt.scatter(t, airmass, label = 'intrinsic_airmass', alpha = 0.5)
    plt.errorbar(comparison_airmass[:,0], comparison_airmass[:,1], comparison_airmass[:,2], fmt = 'ro', label = 'comparison_airmass', alpha = 0.5)
    plt.legend()
    
    # mean of airmass less star 
    mean_aml_plt = plt.figure("mean of airmass less star", figsize = (8, 3), dpi = 100)
    plt.title('mean of airmass less star')
    plt.ylabel('flux')
    plt.xlabel('time')
    plt.errorbar(mean_aml[:,0], mean_aml[:,1], yerr = mean_aml[:,2], fmt = 'ro', label = 'mean of airmass less star')
    plt.legend()
    plt.show()

    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
