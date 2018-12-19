#!/usr/bin/python
'''
Program:
    This is a program for doing photometry on observation data table. 
Usage: 
    photometry.py [phot type ] [start date] [end date]
    
    The input table should follow the form in TAT_env.obs_data_titles

Editor:
    Jacob975
20181029
#################################
update log
20181029 version alpha 1:
    1. The code works
20181205 version alpha 2:
    1. Add an option for choosing a method of photometry you like.
'''
from sys import argv
import numpy as np
import time
import photometry_lib
from mysqlio_lib import TAT_auth, save2sql_EP, save2sql_CATA, find_source_match_coords
import TAT_env
from astropy.time import Time
import matplotlib.pyplot as plt
from test_EP import flux2mag
import collections

def take_data_within_duration(start_date, end_date):
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
    print 'start JD : {0}'.format(start_jd)
    print 'end JD: {0}'.format(end_jd)
    cursor.execute('select * from {0} where JD between {1} and {2}'.format(TAT_env.obs_data_tb_name, start_jd, end_jd))
    data = cursor.fetchall()
    data = np.array(data)
    cursor.close()
    cnx.close()
    return data

def EP_process(data):
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
    # Take 15 brightest stars from first frame
    index_Bstar = np.argsort(first_frame_data[:,inst_mag_index])
    Bstar_name_list = first_frame_data[index_Bstar[10:20], target_name_index]
    print Bstar_name_list
    # Take the data of 10B star from all frames.
    Bstar_jndex = np.where(data[:,target_name_index] == Bstar_name_list[0])
    fileID_index = TAT_env.obs_data_titles.index("FILEID")
    fileIDs = data[Bstar_jndex, fileID_index] 
    source_fileID_list = []
    interception_fileID = None
    # Find the common file ID for 10 bright sources.
    for i in range(len(Bstar_name_list)):
        Bstar_jndex = np.where(data[:, target_name_index] == Bstar_name_list[i])
        data2 = data[Bstar_jndex]
        found_jndex = np.isin(data2[:,fileID_index], fileIDs)
        current_fileIDs = data2[found_jndex, fileID_index]
        print current_fileIDs
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
        Bstar_jndex = np.where(data[:, target_name_index] == Bstar_name_list[i])
        data2 = data[Bstar_jndex]
        # Check if the number of found sources is repeated?
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
    print 'final intercepted file ID'
    print interception_fileID
    #----------------------------------------
    # Do photometry on 10BS only, save the result.
    source_data_array = np.array(source_data_list)
    stu = photometry_lib.EP(source_data_array[0], source_data_array)
    ems, var_ems, m0s, var_m0s = stu.make_airmass_model()
    #----------------------------------------
    # Pick a image, find the center position. 
    cnx = TAT_auth()
    cursor = cnx.cursor()
    cursor.execute('select * from data_file where `ID` = {0}'.format(fileIDs[0][0]))
    img_data = cursor.fetchall()
    cursor.close()
    cnx.close()
    img_ra_cntr = float(img_data[0][4])
    img_dec_cntr = float(img_data[0][5])
    # Get all possible target within the region.
    observed_targets = find_source_match_coords(img_ra_cntr, img_dec_cntr, margin = 0.5)
    # Pick a target star, we make a photometry on it.
    for source in observed_targets:
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
            print 'phot fail'
            continue
        observation_data_ID = observation_data_ID[matched]
        save2sql_EP(correlated_target, observation_data_ID)
        #----------------------------------------
        # Do photometry on 10BS + target, save the result for the target only, and so on.
    return False

# find the corresponding filter with fileID
def find_filter(fileID):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    cursor.execute("select `FILTER` from TAT.data_file where ID='{0}'".format(fileID))
    data = cursor.fetchall()
    data = np.array(data).flatten()
    ans = data[0]
    cursor.close()
    cnx.close()
    return ans

def CATA_process(data):
    #----------------------------------------
    # Save the index of some parameters 
    fileID_index = TAT_env.obs_data_titles.index("FILEID")
    ID_index = TAT_env.obs_data_titles.index('ID')
    #----------------------------------------
    # Load data frame by frame
    fileID_array = np.unique(data[:,fileID_index])
    for fileID in fileID_array:
        frame_data = data[data[:,fileID_index] == fileID]
        #filter_ = find_filter(fileID)
        filter_ = 'V'
        stu = photometry_lib.CATA(frame_data, filter_)
        failure = stu.make_airmass_model()
        if failure:
            print 'air mass model fail.'
            continue
        mag, err_mag = stu.phot()
        mag_array = np.transpose(np.array([mag, err_mag]))
        observation_data_ID = frame_data[:,ID_index]
        # save the result into database
        save2sql_CATA(mag_array, observation_data_ID)
    return False
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Laod argv
    if len(argv) != 4:
        print 'Error!'
        print 'The number of arguments is wrong.'
        print 'Usage: photometry.py [phot type] [start_jd] [end_jd]'
        print 'Available [phot type ]: EP, CATA'
        print 'Example: phototmetry.py EP 20180909 20180910'
        exit()
    phot_type = argv[1]
    start_date = argv[2]
    end_date = argv[3]
    #----------------------------------------
    data = take_data_within_duration(start_date, end_date)
    if phot_type == 'EP':
        failure = EP_process(data)
    elif phot_type == 'CATA':
        failure = CATA_process(data)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
