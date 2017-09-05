#!/usr/bin/python
'''
Program:
This is a program copied and modified from http://docs.astropy.org/en/stable/modeling/. 
Usage:
1. mod_and_fit.py
editor Jacob975
20170905
#################################
update log

20170905 version alpha 1
    1.  It run properly
'''
import time
import numpy as np
from astropy.modeling import models, fitting
#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # set up g as a gaussian model
    g = models.Gaussian1D(amplitude=1.2, mean=0.9, stddev=0.5)
    print(g)
    # setup a linspace between 0.5 to 1.5 by 7 lines
    print g(np.linspace(0.5, 1.5, 7))
    
    #----------------------------
    # we could setup two model by list
    g = models.Gaussian1D(amplitude=[1, 2], mean=[0, 0], stddev=[0.1, 0.2], n_models=2)
    print(g)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
