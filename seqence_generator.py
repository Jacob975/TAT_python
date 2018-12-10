#!/usr/bin/python
'''
Program:
    This is a program to generate a seqence of the given file 
Usage: 
    sequence_generator.py [given file]
Editor:
    Jacob975
20171207
#################################
update log
20181207 version alpha 1:
    1. The code works.
'''
import numpy as np
import time
from sys import argv

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print 'The number of arguments is wrong.'
        print 'Usage: sequence_generator.py [given file]'
        exit()
    data_name = argv[1]
    #---------------------------------------
    # Load data
    data = np.loadtxt(data_name, dtype = str)
    #---------------------------------------
    # Save the seqence
    for i in range(len(data)):
        np.savetxt('seqence_{0}.txt'.format(i+1), data[:i+1], fmt = '%s')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
