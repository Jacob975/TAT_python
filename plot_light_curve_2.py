#!/usr/bin/python
'''
Program:
    This is a program to plot the light curve. 
Usage: 
    plot_light_curve.py [option file] 

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
import photometry

def take_data_within(name, start_date, end_date):
    #----------------------------------------
    # Convert date to JD
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
    print 'band: {0}, exptime = {1}'.format(band, exptime)
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
    data = np.array(data, dtype = object)
    print(data.shape)
    return data

def select_data_by_bands_exptime(data, start_date, end_date, band, exptime):
    #----------------------------------------
    # Convert date to JD
    times = ['{0}-{1}-{2}T12:00:00'.format(start_date[:4], start_date[4:6], start_date[6:]), 
             '{0}-{1}-{2}T12:00:00'.format(end_date[:4], end_date[4:6], end_date[6:])]
    t = Time(times, format='isot', scale='utc')
    start_jd = t.jd[0] 
    end_jd = t.jd[1]
    #----------------------------------------
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # Take the ID of selected images. 
    if band == 'skip' and exptime == 'skip':
        print ('No band and exptime selection.')
        return data
    elif band == 'skip':
        print ('Selected by exptime.')
        band_selection = ''
        exptime_selection = 'and `EXPTIME` = {0}'.format(exptime)
        cursor.execute('select `ID` from {0} where `JD` between {1} and {2}\
                        {3} {4}'
                        .format(TAT_env.im_tb_name,
                                start_jd,
                                end_jd,
                                band_selection,
                                exptime_selection
                                ))
    elif exptime == 'skip':
        print ('Selected by bands.')
        band_selection = 'and `FILTER` = "{0}"'.format(band)
        exptime_selection = ''
        cursor.execute('select `ID` from {0} where `JD` between {1} and {2}\
                        {3} {4}'
                        .format(TAT_env.im_tb_name,
                                start_jd,
                                end_jd,
                                band_selection,
                                exptime_selection
                                ))
    else:
        print ('Selected by bands and exptime.')
        cursor.execute('select `ID` from {0} where `JD` between {1} and {2}\
                        and `FILTER` = "{3}"\
                        and `EXPTIME` = {4}'
                        .format(TAT_env.im_tb_name,
                                start_jd,
                                end_jd,
                                band,
                                exptime
                                ))
    selected_image_ID = cursor.fetchall()
    cursor.close()
    cnx.close()
    # Selected by Bands and Exposure Time.
    selected_image_ID = np.array(selected_image_ID)
    ID_index = TAT_env.obs_data_titles.index('FILEID')
    selected_data = []
    for source in data:
        dummy_index = np.where(selected_image_ID == source[ID_index])
        if len(dummy_index[0]) >= 1:
            selected_data.append(source)
    selected_data = np.array(selected_data, dtype = object)
    print ('data points: {0}'.format(len(selected_data)))
    return selected_data


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
        print 'Usage: plot_light_curve_2.py [option_file]' 
        stu.create()
        exit()
    options = argv[1]
    where_they_from,\
    data_name,\
    ingress,\
    egress,\
    start_date,\
    end_date,\
    band,\
    exptime, = stu.load(options)
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
        data = take_data_within(data_name, 
                                start_date, 
                                end_date)
        data = np.array(data, dtype = object)
        data = select_data_by_bands_exptime(data, start_date, end_date, band, exptime)
    elif where_they_from == 2 and start_date == 'skip':
        data = load_data(data_name)    
        data = np.array(data, dtype = object)
        data = select_data_by_bands_exptime(data, start_date, end_date, band, exptime)
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
    JD_array =          np.array(data[:,index_JD], dtype = float)
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
    axs.set_title('The light curve of {0} in {1} band {2} secs'.format(data_name, band, exptime))
    axs.set_xlabel('JD')
    axs.set_ylabel('Flux Percentage')
    axs.set_xlim(np.amin(JD_array)-x_margin, np.amax(JD_array)+x_margin)
    axs.set_ylim( \
        np.nanmedian(EP_MAG_array) - y_margin, 
        np.nanmedian(EP_MAG_array) + y_margin,
        )
    axs.grid(True)
    if timing != 'skip':
        axs.plot([ingress, ingress],
                    [np.nanmedian(EP_MAG_array)-y_margin, np.nanmedian(EP_MAG_array)+y_margin],
                    zorder=2, label = 'Ingress time')
        axs.plot([egress, egress],
                    [np.nanmedian(EP_MAG_array)-y_margin, np.nanmedian(EP_MAG_array)+y_margin],
                    zorder=1, label = 'Egress time')
    axs.errorbar(JD_array, EP_MAG_array, yerr = E_EP_MAG_array, fmt = 'ro', label = data_name, markersize = 3, zorder=3)
    plt.legend()
    plt.savefig('light_curve.png')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
