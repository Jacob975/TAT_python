#!/usr/bin/python
'''
Program:
This is a program copied and modified from http://docs.astropy.org/en/stable/modeling/
Usage:
1. fit_1DcompoundGaussian_example.py
editor Jacob975
20170905
#################################
update log

20170905 version alpha 1
'''
import numpy as np
import time
import numpy as np
import matplotlib.pyplot as plt
from astropy.modeling import models, fitting

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # Generate fake data
    np.random.seed(42)
    g1 = models.Gaussian1D(1, 0, 0.2)
    g2 = models.Gaussian1D(2.5, 0.5, 0.1)
    x = np.linspace(-1, 1, 200)
    y = g1(x) + g2(x) + np.random.normal(0., 0.2, x.shape)

    # Now to fit the data create a new superposition with initial
    # guesses for the parameters:
    gg_init = models.Gaussian1D(1, 0, 0.1) + models.Gaussian1D(2, 0.5, 0.1)
    fitter = fitting.SLSQPLSQFitter()
    gg_fit = fitter(gg_init, x, y)

    # Plot the data with the best-fit model
    result_fig = plt.figure(figsize=(8,5))
    plt.plot(x, y, 'ko')
    plt.plot(x, gg_fit(x))
    plt.xlabel('Position')
    plt.ylabel('Flux')
    result_fig.show()
    raw_input()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."