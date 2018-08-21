#!/usr/bin/python
'''
Program:
    This is a test for understanding how to use joblib, a module in python. 
Usage: 
    test_joblib.py
Editor:
    Jacob975
20170216
#################################
update log
20180821 version alpha 1
    1. The code works.
'''
import time
from joblib import Parallel, delayed

# A function that can be called to do work:
def work(arg):    
    print "Function receives the arguments as a list:", arg
    # Split the list to individual variables:
    i, j = arg    
    # All this work function does is wait 1 second...
    time.sleep(1)    
    # ... and prints a string containing the inputs:
    print "%s_%s" % (i, j)
    return "%s_%s" % (i, j)

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # List of arguments to pass to work():
    arg_instances = [(1, 1), (1, 2), (1, 3), (1, 4)]
    # Anything returned by work() can be stored:
    results = Parallel(n_jobs=4, verbose=1, backend="threading")(map(delayed(work), arg_instances))
    print results
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
