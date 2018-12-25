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
    if len(argv) != 3:
        print 'The number of arguments is wrong.'
        print 'Usage: plot_limiting_mag.py [file low] [file high]' 
        exit()
    file_name_low = argv[1]
    file_name_high = argv[2]
    #---------------------------------------
    # Load data in low altitude
    data_low = np.loadtxt(file_name_low, dtype = str)
    lim_mag_low = np.array(data_low[:,1], dtype = float)
    x_lin_low = 150 * (np.arange(len(lim_mag_low)) + 2)
    # Load data in high altitude
    data_high = np.loadtxt(file_name_high, dtype = str)
    lim_mag_high = np.array(data_high[:,1], dtype = float)
    x_lin_high = 150 * (np.arange(len(lim_mag_high)) + 2)
    #---------------------------------------
    plt.title('The limiting magnitude(V band)')
    plt.xlabel('exposure time(second)')
    plt.ylabel('The limiting magnitude')
    plt.grid(True)
    plt.plot(x_lin_low, lim_mag_low, c = 'r', label = 'The Altitude range from $37^{\circ}$ to $53^{\circ}$', )
    plt.plot(x_lin_high, lim_mag_high, c = 'b', label = 'The Altitude range from $55^{\circ}$ to $90^{\circ}$')
    plt.legend()
    plt.savefig('limiting_mag.png')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
