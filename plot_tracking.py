#!/usr/bin/python
'''
Program:
    This is a program to plot the track of a star on frames. 
Usage: 
    plot_tracking.py [files]

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
import TAT_env
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print 'The number of arguments is wrong.'
        print 'Usage: plot_tracking.py [file]' 
        exit()
    file_name = argv[1]
    #---------------------------------------
    # Load data
    data = np.loadtxt(file_name, dtype = str)
    x_track = np.array(data[:,1], dtype = float) - float(data[0,1])
    y_track = np.array(data[:,3], dtype = float) - float(data[0,3])
    pixel_coord = np.transpose(np.array([x_track*TAT_env.pix1, y_track*TAT_env.pix1]))
    tot_track = np.sqrt(np.power(x_track, 2) + np.power(y_track, 2))*TAT_env.pix1
    time_lin = (np.arange(len(tot_track)) +1 ) * 150.
    # Find the scale of the offset.
    scale = x_track[-1]*TAT_env.pix1
    if abs(x_track[-1]) < abs(y_track[-1]):
        scale = y_track[-1]*TAT_env.pix1
    #---------------------------------------
    fig, axs = plt.subplots(1, 2, figsize = (12, 6))
    axs = axs.ravel()
    axs[0].set_title('Tracking offset(WASP 11 b)')
    axs[0].grid(True)
    axs[0].scatter(pixel_coord[:,0], pixel_coord[:,1], c= 'g', marker = '+')
    axs[0].scatter(pixel_coord[0,0], pixel_coord[0, 1], c = 'r', label = 'start point')
    axs[0].scatter(pixel_coord[-1,0],pixel_coord[-1, 1], c = 'b', label = 'end point')
    axs[0].set_xlabel('x offset(arcsec)')
    axs[0].set_ylabel('y offset(arcsec)')
    axs[0].legend()
    # set the scale
    if x_track[-1] > 0 and y_track[-1] > 0:
        print '1'
        axs[0].set_xlim(-10, scale+10)
        axs[0].set_ylim(-10, scale+10)
    elif x_track[-1] > 0 and y_track[-1] < 0:
        print '2'
        axs[0].set_xlim(-10, scale+10)
        axs[0].set_ylim(scale-10, 10)
    elif x_track[-1] < 0 and y_track[-1] < 0:
        print '3'
        axs[0].set_xlim(scale-10+100, 10+100)
        axs[0].set_ylim(scale-10, 10)
    elif x_track[-1] < 0 and y_track[-1] > 0:
        print '4'
        axs[0].set_xlim(scale-10, 10)
        axs[0].set_ylim(-10, scale+10)
    
    axs[1].set_title('Tracking stability(WASP 11 b)')
    axs[1].grid(True)
    axs[1].scatter(time_lin, tot_track, c= 'g', marker = '+')
    axs[1].set_ylabel('total offset(arcsec)')
    axs[1].set_xlabel('time(sec)')
    fig.savefig('The_track.png')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
