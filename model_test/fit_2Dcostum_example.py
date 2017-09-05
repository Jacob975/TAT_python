#!/usr/bin/python
'''
Program:
This is a program copied and modified from http://docs.astropy.org/en/stable/modeling/new.html
Usage:
1. fit_2Dcustom_example.py
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

class SLSQPFitter(Fitter):
    supported_constraints = ['bounds', 'eqcons', 'ineqcons', 'fixed', 'tied']

    def __init__(self):
        # Most currently defined fitters take no arguments in their
        # __init__, but the option certainly exists for custom fitters
        super(SLSQPFitter, self).__init__()

    def objective_function(self, fps, *args):
        model = args[0]
        meas = args[-1]
        model.fitparams(fps)
        res = self.model(*args[1:-1]) - meas
        return np.sum(res**2)

    def __call__(self, model, x, y , maxiter=MAXITER, epsilon=EPS):
        if model.linear:
                raise ModelLinearityException(
                    'Model is linear in parameters; '
                    'non-linear fitting methods should not be used.')
        model_copy = model.copy()
        init_values, _ = _model_to_fit_params(model_copy)
        self.fitparams = optimize.fmin_slsqp(self.errorfunc, p0=init_values,
                                         args=(y, x),
                                         bounds=self.bounds,
                                         eqcons=self.eqcons,
                                         ineqcons=self.ineqcons)
        return model_copy
#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
