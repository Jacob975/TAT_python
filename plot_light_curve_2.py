#!/usr/bin/python
'''
Program:
    This is a program to plot the light curve. 
Usage: 
    plot_light_curve.py [where they from?] [target name]

    [where they from?]
        1: from a text file
        2: from database `observation_data`

Editor:
    Jacob975
20181129
#################################
update log

20181129 version alpha 1
'''
from sys import argv
import numpy as np
import time
from mysqlio_lib import TAT_auth
import TAT_env
import matplotlib.pyplot as plt
from reduction_lib import header_editor
from input_lib import option_plotLC

def load_data(name):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    cursor.execute('select * from observation_data where `NAME` = "{0}"'.format(name))
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    stu = option_plotLC()
    if len(argv) != 2:
        print 'The number of arguments is wrong.'
        print 'Usage: plot_light_curve.py [option_file]' 
        stu.create()
        exit()
    options = argv[1]
    where_they_from, data_name, ingress, egress = stu.load(options)
    where_they_from = int(where_they_from)
    timing = 'OK'
    if ingress == 'skip' or egress == 'skip':
        print 'skip timing'
        timing = 'skip'
    else:
        ingress = float(ingress)
        egress = float(egress)
    #---------------------------------------
    # Load data
    data = None
    if where_they_from == 2:
        data = load_data(data_name)
        data = np.array(data, dtype = object)
    elif where_they_from == 1:
        data = np.loadtxt(data_name, dtype = object)
    #---------------------------------------
    # Get the JD, EP_MAG, and E_EP_MAG, plot the light curve.
    index_RA = TAT_env.obs_data_titles.index('RA')
    index_DEC = TAT_env.obs_data_titles.index('`DEC`')
    index_JD = TAT_env.obs_data_titles.index('JD')
    index_EP_MAG = TAT_env.obs_data_titles.index('EP_MAG')
    index_E_EP_MAG = TAT_env.obs_data_titles.index('E_EP_MAG')
    index_INST_MAG = TAT_env.obs_data_titles.index('INST_MAG')
    index_E_INST_MAG = TAT_env.obs_data_titles.index('E_INST_MAG')
    JD_array =         np.array(data[:,index_JD], dtype = float)
    EP_MAG_array =      np.array(data[:,index_EP_MAG], dtype = float)
    E_EP_MAG_array =    np.array(data[:,index_E_EP_MAG], dtype = float)
    # Convert mag to delta mag
    EP_MAG_array = np.mean(EP_MAG_array[-10:]) - EP_MAG_array 
    # Convert delta mag to percentage
    EP_MAG_array = np.power(10.0, EP_MAG_array/2.5)
    #---------------------------------------
    x_margin = 0.02
    y_margin = 0.05
    fig, axs = plt.subplots(1, 1, figsize = (12, 6))
    #axs.set_title('The light curve of {0}'.format(data_name))
    axs.set_title('The light curve of WASP 36 b')
    axs.set_xlabel('JD')
    axs.set_ylabel('Flux Percentage')
    axs.set_xlim(JD_array[0]-x_margin, JD_array[-1]+x_margin)
    axs.set_ylim( \
        np.median(EP_MAG_array[~np.isnan(EP_MAG_array)]) - y_margin, 
        np.median(EP_MAG_array[~np.isnan(EP_MAG_array)]) + y_margin,
        )
    axs.grid(True)
    axs.errorbar(JD_array, EP_MAG_array, yerr = E_EP_MAG_array, fmt = 'ro', label = 'WASP 36 b, Vmag = 12.7')
    if timing != 'skip':
        axs.plot([ingress, ingress],
                    [np.median(EP_MAG_array[~np.isnan(EP_MAG_array)])-y_margin, np.median(EP_MAG_array[~np.isnan(EP_MAG_array)])+y_margin],)
        axs.plot([egress, egress],
                    [np.median(EP_MAG_array[~np.isnan(EP_MAG_array)])-y_margin, np.median(EP_MAG_array[~np.isnan(EP_MAG_array)])+y_margin],)
    plt.legend()
    plt.savefig('light_curve.png')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."