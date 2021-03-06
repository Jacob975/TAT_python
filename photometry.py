#!/usr/bin/python
'''
Program:
    This is a program for doing photometry on observation data table. 
Usage: 
    photometry.py [option file]
    
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
from input_lib import option_photometry

def take_data_within(start_date, end_date, ra_cntr_str, dec_cntr_str):
    #----------------------------------------
    times = ['{0}-{1}-{2}T12:00:00'.format(start_date[:4], start_date[4:6], start_date[6:]), 
             '{0}-{1}-{2}T12:00:00'.format(end_date[:4], end_date[4:6], end_date[6:])]
    t = Time(times, format='isot', scale='utc')
    start_jd = t.jd[0] 
    end_jd = t.jd[1]
    ra_cntr = float(ra_cntr_str)
    dec_cntr = float(dec_cntr_str)
    #----------------------------------------
    # Query data
    cnx = TAT_auth()
    cursor = cnx.cursor()
    print 'start JD : {0}'.format(start_jd)
    print 'end JD : {0}'.format(end_jd)
    print "Center at ({0}, {1})".format(ra_cntr, dec_cntr)
    print "band: {0}, exptime : {1}".format(band, exptime)
    print 'Start ID : {0}, Numbers of aux star : {1}'.format(begin_of_aux, no_of_aux)
    # Selected by Coordinate.
    cursor.execute('select * from {0} where `JD` between {1} and {2} \
                    and `RA` between {3} and {4} \
                    and `DEC` between {5} and {6}'\
                    .format(TAT_env.obs_data_tb_name, 
                            start_jd, 
                            end_jd, 
                            ra_cntr-0.5, 
                            ra_cntr+0.5, 
                            dec_cntr-0.5, 
                            dec_cntr+0.5
                            ))
    data = cursor.fetchall()
    data = np.array(data)
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
    selected_data = np.array(selected_data)
    return selected_data

def EP_process(data):
    #----------------------------------------
    # Load the index of some parameters 
    bjd_index = TAT_env.obs_data_titles.index('BJD')
    inst_mag_index = TAT_env.obs_data_titles.index('INST_MAG')
    e_inst_mag_index = TAT_env.obs_data_titles.index('E_INST_MAG')
    target_name_index = TAT_env.obs_data_titles.index('NAME')
    fileID_index = TAT_env.obs_data_titles.index("FILEID")
    #----------------------------------------
    # Pick several brightest stars from each frame 
    # They have to be the same set of stars in diff. frames.)
    
    # Take all the data in the first frame
    first_bjd = np.amin(data[:, bjd_index])
    first_frame_data = data[data[:,bjd_index] == first_bjd]
    # Sort the first frame data by the brightness 
    first_frame_data = first_frame_data[np.argsort(first_frame_data[:,inst_mag_index])]
    # Take the data from all frames.
    all_fileIDs = data[:,fileID_index]
    fileIDs = [item for item, count in collections.Counter(all_fileIDs).items() if count > 1] 
    source_list = []
    selected_source_name = []
    # Find sources found in all frames.
    for source in first_frame_data[int(begin_of_aux):]:
        if len(source_list) >= int(no_of_aux):
            break
        if source[target_name_index] == var_star:
            #print ("Skipped, it is an var star")
            continue
        source_data = data[data[:,target_name_index] == source[target_name_index]]
        source_fileIDs = source_data[:,fileID_index]
        #print ('# of A frames: {0}, # of B frames: {1}'.format(len(source_fileIDs), len(fileIDs)))
        if len(source_fileIDs) == len(fileIDs):
            #print ("Take it")
            source_error = source_data[:, e_inst_mag_index]
            source_error[source_error == 0.0] = 1e-4
            source_data_lite = np.transpose(np.array([source_data[:, bjd_index], 
                                                    source_data[:, inst_mag_index], 
                                                    source_error])) 
            source_list.append(source_data_lite)
            selected_source_name.append(source[target_name_index])
            continue
        else:
            #print ("Abort it")
            continue
    #----------------------------------------
    # Do photometry on Bright Stars only, save the result.
    source_data_array = np.array(source_list)
    print (np.array(selected_source_name))
    print (source_data_array.shape)
    stu = photometry_lib.EP(source_data_array[0], source_data_array)
    ems, var_ems, m0s, var_m0s = stu.make_airmass_model()

    #----------------------------------------
    # Pick a image, find the center position. 
    cnx = TAT_auth()
    cursor = cnx.cursor()
    print (fileIDs)
    cursor.execute('select * from {0} where `ID` = {1}'.format(TAT_env.im_tb_name, fileIDs[0]))
    img_data = cursor.fetchall()
    cursor.close()
    cnx.close()
    img_ra_cntr = float(img_data[0][4])
    img_dec_cntr = float(img_data[0][5])
    # Get all possible target within the region.
    observed_targets = find_source_match_coords(img_ra_cntr, img_dec_cntr, margin = TAT_env.pix1*1024./3600.)
    # Pick a target star, we make a photometry on it.
    for source in observed_targets:
        # Take the name of the source
        source_name = source[target_name_index]
        # Get the data of the source from original dataset.
        data2 = data[np.isin(data[:,target_name_index], source_name)]
        # Take the ID, time, magnitude, and uncertainties. 
        observation_data_ID = data2[:,0]
        time_array          = data2[:, bjd_index]
        mag_array           = data2[:, inst_mag_index]
        err_mag_array       = data2[:, e_inst_mag_index] 
        # Combine and do EP phot.
        source_data = np.transpose(np.array([time_array, mag_array, err_mag_array]))
        failure, correlated_target, matched = stu.phot(source_data)
        if failure:
            print 'One event {0} cannot be measure.'.format(source_name)
            continue
        observation_data_ID = observation_data_ID[matched]
        save2sql_EP(correlated_target, observation_data_ID)
    return False

# find the corresponding filter with fileID
def find_filter(fileID):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    cursor.execute("select `FILTER` from TAT.{0} where ID='{1}'".format(
        TAT_env.im_tb_name, 
        fileID))
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
        # Take all extracted sources on that frame.
        frame_src_data = data[data[:,fileID_index] == fileID]
        _filter = find_filter(fileID)
        stu = photometry_lib.CATA(frame_src_data, _filter)
        failure = stu.make_airmass_model()
        if failure:
            print 'air mass model fail.'
            continue
        mag, err_mag = stu.phot()
        mag_array = np.transpose(np.array([mag, err_mag]))
        observation_data_ID = frame_src_data[:,ID_index]
        # save the result into database
        save2sql_CATA(mag_array, observation_data_ID)
    return 0 
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Laod argv
    stu = option_photometry()
    if len(argv) != 2:
        print 'Error!'
        print 'The number of arguments is wrong.'
        print 'Usage: photometry.py [option file]' 
        print 'You should modify the [option file] before execution.'
        stu.create()
        exit(1)
    options = argv[1]
    phot_type,\
    start_date,\
    end_date,\
    ra_cntr,\
    dec_cntr,\
    band,\
    exptime,\
    begin_of_aux,\
    no_of_aux,\
    var_star = stu.load(options)
    #----------------------------------------
    # Load data
    data = take_data_within(start_date, end_date, ra_cntr, dec_cntr)
    # Sort data by BJD
    bjd_index = TAT_env.obs_data_titles.index('BJD')
    BJD = data[:,bjd_index]
    BJD_index = np.argsort(BJD)
    data = data[BJD_index]
    if phot_type == 'EP':
        failure = EP_process(data)
    elif phot_type == 'CATA':
        failure = CATA_process(data)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
