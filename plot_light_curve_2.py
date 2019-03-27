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
from astropy.time import Time

def take_data_within(name, start_date, end_date):
    #----------------------------------------
    times = ['{0}-{1}-{2}T12:00:00'.format(start_date[:4], start_date[4:6], start_date[6:]), 
             '{0}-{1}-{2}T12:00:00'.format(end_date[:4], end_date[4:6], end_date[6:])]
    t = Time(times, format='isot', scale='utc')
    start_jd = t.jd[0] 
    end_jd = t.jd[1]
    #----------------------------------------
    # Query data
    cnx = TAT_auth()
    cursor = cnx.cursor()
    print 'target: {0}'.format(name)
    print 'start JD : {0}'.format(start_jd)
    print 'end JD: {0}'.format(end_jd)
    cursor.execute('select * from {0} where `NAME` = "{1}" \
                    and `JD` between {2} and {3}'\
                    .format(TAT_env.obs_data_tb_name, name, start_jd, end_jd))
    data = cursor.fetchall()
    data = np.array(data)
    cursor.close()
    cnx.close()
    return data

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
    where_they_from, data_name, ingress, egress, start_date, end_date = stu.load(options)
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
    if where_they_from == 2 and start_date != 'skip':
        data = take_data_within(data_name, start_date, end_date)
        data = np.array(data, dtype = object)
    elif where_they_from == 2 and start_date == 'skip':
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
    EP_MAG_mean = np.mean(EP_MAG_array[-10:])
    if np.isnan(EP_MAG_mean):
        EP_MAG_mean = np.mean(EP_MAG_array[:10])
    EP_MAG_array = EP_MAG_mean - EP_MAG_array 
    
    # Convert delta mag to percentage
    EP_MAG_array = np.power(10.0, EP_MAG_array/2.5)
    #---------------------------------------
    x_margin = 0.02
    y_margin = 0.05
    fig, axs = plt.subplots(1, 1, figsize = (12, 6))
    #axs.set_title('The light curve of {0}'.format(data_name))
    axs.set_title('The light curve of {0}'.format(data_name))
    axs.set_xlabel('JD')
    axs.set_ylabel('Flux Percentage')
    axs.set_xlim(JD_array[0]-x_margin, JD_array[-1]+x_margin)
    axs.set_ylim( \
        np.nanmedian(EP_MAG_array) - y_margin, 
        np.nanmedian(EP_MAG_array) + y_margin,
        )
    axs.grid(True)
    if timing != 'skip':
        axs.plot([ingress, ingress],
                    [np.nanmedian(EP_MAG_array)-y_margin, np.nanmedian(EP_MAG_array)+y_margin],
                    zorder=2)
        axs.plot([egress, egress],
                    [np.nanmedian(EP_MAG_array)-y_margin, np.nanmedian(EP_MAG_array)+y_margin],
                    zorder=1)
    axs.errorbar(JD_array, EP_MAG_array, yerr = E_EP_MAG_array, fmt = 'ro', label = data_name, markersize = 3, zorder=3)
    plt.legend()
    plt.savefig('light_curve.png')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
