#!/usr/bin/python
'''
Program:
    This is a test program for autocorrelation 
Usage: 
    test_autocorrelation.py
Editor:
    Jacob975
20181127
#################################
update log
'''
import numpy as np
import time
import matplotlib.pyplot as plt
from uncertainties import unumpy, ufloat

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

def autocorr(x):
    # Compute the autocorrelation of the signal, based on the properties of the
    # power spectral density of the signal.
    xp = x-np.mean(x)
    f = np.fft.fft(xp)
    p = np.array([np.real(v)**2+np.imag(v)**2 for v in f])
    pi = np.fft.ifft(p)
    return np.real(pi)[:x.size/2]/np.sum(xp**2)
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Period
    T = 50
    term = 500
    # standard deviation
    stdev = 2
    # Model a Target Star 
    # Sine wave (radian)
    t = np.arange(term)
    intrinsic = np.sin(2 * np.pi * t / T) + 10
    intrinsic_mag, _ = flux2mag(intrinsic, stdev)
    uncertainties = np.random.normal(0, stdev, term)
    flux = intrinsic + uncertainties
    mag, err_mag = flux2mag(flux, stdev)
    target = np.transpose([ t, mag, err_mag])
    correlation = autocorr(mag)
    #----------------------------------------
    # Plot the answers
    # target
    target_plt = plt.figure("target", figsize=(9, 6), dpi=100)
    
    plt.subplot(3, 1, 1)
    plt.title('intrinsic_target')
    plt.xlabel('time')
    plt.ylabel('mag')
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_visible(False)
    plt.plot(t, intrinsic_mag, label = 'intrinsic_target')
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.title('observed_target')
    plt.xlabel("time")
    plt.ylabel('mag')
    frame1 = plt.gca()
    frame1.axes.get_xaxis().set_visible(False)
    plt.errorbar(target[:,0], target[:,1], yerr = target[:,2], fmt = 'ro', alpha = 0.5, label = 'observed_target')
    plt.legend()
    
    plt.subplot(3, 1, 3)
    plt.title('autocorrelation')
    plt.ylabel('R')
    plt.xlabel('time')
    plt.bar(t[1:t.size/2], correlation[1:], label = 'correlation')
    plt.legend()
    
    plt.show()
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
