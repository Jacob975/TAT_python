#!/usr/bin/python
'''
Program:
    This is a program to plot the limiting mag. 
Usage: 
    plot_limiting_mag.py [files]

Editor:
    Jacob975
20181218
#################################
update log

20181218 version alpha 1
    1. The code works
'''
from sys import argv
import numpy as np
import time
import matplotlib.pyplot as plt

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print 'The number of arguments is wrong.'
        print 'Usage: plot_limiting_mag.py [file]' 
        exit()
    file_name = argv[1]
    #---------------------------------------
    # Load data
    data = np.loadtxt(file_name, dtype = str)
    lim_mag = np.array(data[:,1], dtype = float)
    x_lin = 150 * (np.arange(len(lim_mag)) + 2)
    #---------------------------------------
    plt.title('The limiting magnitude(V band)')
    plt.xlabel('exposure time(second)')
    plt.ylabel('The limiting magnitude')
    plt.grid(True)
    plt.plot(x_lin, lim_mag, label = 'The Altitude range from $55^{\circ}$ to $90^{\circ}$')
    plt.legend()
    plt.savefig('limiting_mag.png')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
