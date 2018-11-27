#!/usr/bin/python
'''
Program:
    This is a program for doing photometry on observation data table. 
Usage: 
    photometry.py [start date] [end date]
    
    The input table should follow the form in TAT_env.obs_data_titles

Editor:
    Jacob975
20181029
#################################
update log
20181029 version alpha 1:
    1. The code works
'''
from sys import argv
import numpy as np
import time
import photometry_lib
from mysqlio_lib import TAT_auth, save2sql_EP
import TAT_env
from astropy.time import Time
import matplotlib.pyplot as plt
from test_EP import flux2mag
import collections

def EP_process(start_jd, end_jd):
    #----------------------------------------
    # Query data
    cnx = TAT_auth()
    cursor = cnx.cursor()
    cursor.execute('select * from {0} where JD between {1} and {2}'.format(TAT_env.obs_data_tb_name, start_jd, end_jd))
    data = cursor.fetchall()
    data = np.array(data)
    #----------------------------------------
    # Save the index of some parameters 
    bjd_index = TAT_env.obs_data_titles.index('BJD')
    inst_mag_index = TAT_env.obs_data_titles.index('INST_MAG')
    e_inst_mag_index = TAT_env.obs_data_titles.index('E_INST_MAG')
    target_name_index = TAT_env.obs_data_titles.index('NAME')
    fileID_index = TAT_env.obs_data_titles.index("FILEID")
    # Pick 10 brightest stars from each frame (They have to be the same star in diff. frames.)
    # Take all the data in the first frame
    first_bjd = data[0, bjd_index]
    index_data_in_first_frame = np.where(data[:,bjd_index] == first_bjd)
    first_frame_data = data[index_data_in_first_frame]
    # Take 10 brightest stars from first frame
    index_10Bstar = np.argsort(first_frame_data[:,inst_mag_index])
    Bstar_10_name_list = first_frame_data[index_10Bstar[:10], target_name_index]
    # Take the data of 10B star from all frames.
    Bstar_jndex = np.where(data[:,target_name_index] == Bstar_10_name_list[0])
    fileID_index = TAT_env.obs_data_titles.index("FILEID")
    fileIDs = data[Bstar_jndex, fileID_index] 
    source_fileID_list = []
    interception_fileID = None
    # Find the common file ID for 10 bright sources.
    for i in range(len(Bstar_10_name_list)):
        Bstar_jndex = np.where(data[:, target_name_index] == Bstar_10_name_list[i])
        data2 = data[Bstar_jndex]
        found_jndex = np.isin(data2[:,fileID_index], fileIDs)
        current_fileIDs = data2[found_jndex, fileID_index]
        # Find the common file ID compare to the previous one.
        if i == 0:
            interception_fileID = current_fileIDs 
        else:
            interception_fileID = np.intersect1d(interception_fileID, current_fileIDs) 
        source_fileID_list.append(current_fileIDs)
    # Remove the frame misses one or more stars.
    source_data_list = []
    # Get the data of 10 bright sources.
    for i in range(len(source_fileID_list)):
        # Get the rows contain a Bright star.
        Bstar_jndex = np.where(data[:, target_name_index] == Bstar_10_name_list[i])
        data2 = data[Bstar_jndex]
        # Check if the number is repeated?
        # If repeat, that means the source is confusing, so I abandan the source.
        repeat_numbers = [item for item, count in collections.Counter(source_fileID_list[i]).items() if count > 1]
        if len(repeat_numbers) != 0:
            continue
        # Take the common frames only
        index_fileIDs = np.isin(source_fileID_list[i], interception_fileID)
        found_jndex = np.isin(data2[:,fileID_index], source_fileID_list[i][index_fileIDs])
        time_array = data2[found_jndex, bjd_index]
        mag_array  = data2[found_jndex, inst_mag_index]
        err_mag_array = data2[found_jndex, e_inst_mag_index] 
        source_data = np.transpose(np.array([time_array, mag_array, err_mag_array], dtype = float))
        source_data_list.append(source_data)
    #----------------------------------------
    # Do photometry on 10BS only, save the result.
    source_data_array = np.array(source_data_list)
    stu = photometry_lib.EP(source_data_array[0], source_data_array)
    ems, var_ems, m0s, var_m0s = stu.make_airmass_model()
    #----------------------------------------
    # Pick a target star, we make a photometry on it.
    for source in first_frame_data:
        # Take the name of the source
        source_name = source[target_name_index]
        # Get all the data of the source
        data2 = data[np.isin(data[:,target_name_index], source_name)]
        # Take time, magnitude, and error of magnitude.
        observation_data_ID = data2[:,0]
        time_array = data2[:,bjd_index]
        mag_array  = data2[:, inst_mag_index]
        err_mag_array = data2[:, e_inst_mag_index] 
        # Combine and do EP phot.
        source_data = np.transpose(np.array([time_array, mag_array, err_mag_array]))
        failure, correlated_target, matched = stu.phot(source_data)
        if failure:
            continue
        observation_data_ID = observation_data_ID[matched]
        '''
        # plot the result
        fig1, axes = plt.subplots(2, 1, figsize = (12, 8))
        axes = axes.ravel()
        axes[0].set_title("Before EP")
        axes[0].scatter(source_data[:,0], source_data[:,1])
        axes[1].set_title("After EP")
        axes[1].scatter(correlated_target[:,0], correlated_target[:,1])
        plt.show()
        '''
        save2sql_EP(correlated_target, observation_data_ID)
    #----------------------------------------
    # Do photometry on 10BS + target, save the result for the target only, and so on.
    cursor.close()
    cnx.close()
    return False, data

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Laod argv
    if len(argv) != 3:
        print 'Error!'
        print 'The number of arguments is wrong.'
        print 'Usage: photometry.py [start_jd] [end_jd]'
        print 'Example: phototmetry.py 20180909 20180910'
        exit()
    start_date = argv[1]
    end_date = argv[2]
    #----------------------------------------
    iraf_mod_table = 0
    #----------------------------------------
    # Start ensemble photometry.
    times = ['{0}-{1}-{2}T00:00:00'.format(start_date[:4], start_date[4:6], start_date[6:]), 
             '{0}-{1}-{2}T00:00:00'.format(end_date[:4], end_date[4:6], end_date[6:])]
    t = Time(times, format='isot', scale='utc')
    start_jd = t.jd[0] 
    end_jd = t.jd[1]
    failure, iraf_mod_table = EP_process(start_jd, end_jd)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
