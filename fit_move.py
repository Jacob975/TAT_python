#!/usr/bin/python
'''
Program:
This is a program to mathc a list of fits, and move the position of fits to the reference fits. 
reference fits is the first one in the list.
method:
1. fit_move.py [list name]
editor Jacob975
20170422 
#################################
update log
    20170422 version alpah 1
    I haven't come up with a good idea.

    20170507 version alpha 2
    This code contain two main part
    the first part is match stars in two fits by inner prod. relation.
    the second part is regrid the target fits to reference fits.

    20170627 version alpha 3 
    add a new func, if star list is too long to match, 
    limitation of choose star will raise such that decrease the number of stars.

    20170728 version alpha 4
    1.  now it will find ref img automatically.

    20170808 version alpha 5
    1.  use tat_config to control path of result data instead of fix the path in the code.
'''
from sys import argv
import numpy as np
import pyfits
import time
import curvefit
import matplotlib.pyplot as plt
import os
import tat_datactrl

# controll how many thing would be printed. 0 mean no, 1 means nessesary, 2 means debug.
VERBOSE = 3

def regrid_data(data, rotation_matrix_inverse ):
    # construct the translation matrix of two fits
    regrided_data = np.empty(data.shape) 
    pre_coor = np.array([500.0, 500.0, 1.0])
    new_coor = np.dot(rotation_matrix_inverse, pre_coor)
    area = np.array([(1-new_coor[0]%1) * (1-new_coor[1]%1), (new_coor[0]%1) * (1-new_coor[1]%1), (new_coor[0]%1) * (new_coor[1]%1), (1-new_coor[0]%1) * (new_coor[1]%1)])
    del pre_coor
    del new_coor
    # determine the ratio of 2D interpolation method.
    data_a = np.multiply(data, area[0])
    data_b = np.multiply(data, area[1])
    data_c = np.multiply(data, area[2])
    data_d = np.multiply(data, area[3])
    # regriding 
    for x in xrange(data.shape[0]):
        for y in xrange(data.shape[0]):
            pre_coor = (float(x), float(y), 1.0)
            new_coor = np.dot(rotation_matrix_inverse, pre_coor)
            # do regriding, if the position is on border, fill in with nan.
            try:
                regrided_data[x, y] = data_a[int(new_coor[0]),int(new_coor[1])] + data_b[int(new_coor[0])+1,int(new_coor[1])] + data_c[int(new_coor[0])+1,int(new_coor[1])+1] + data_d[int(new_coor[0]),int(new_coor[1])+1]
            except IndexError:
                regrided_data[x,y] = np.nan
    del data_a, data_b, data_c, data_d
    return regrided_data

def create_matched_fits(name, data, mean_delta_x, mean_delta_y):
    imAh=pyfits.getheader(name)
    rotation_matrix_inverse = np.array([[1,0,mean_delta_x],[0,1,mean_delta_y],[0,0,1]], dtype = float)
    regrided_data = regrid_data(data, rotation_matrix_inverse)
    pyfits.writeto(name[0:-5]+'_m.fits',regrided_data,imAh, clobber = True)
    if VERBOSE>0 : print name[0:-5]+"_m.fits OK"

def get_match(ref_star_list, star_list ):
    match_star_list = []
    delta_x_list = np.array([])
    delta_y_list = np.array([])
    # determine how many stars to go match
    b_star_list = star_list[:]
    if VERBOSE>3:
        print "star_list"
        for star in b_star_list:
            print star
    b_ref_star_list = ref_star_list[:]
    # match stars with ref_img by inner prod.
    inner_prod_list, inner_prod_error_list = curvefit.get_inner_product(b_star_list)
    ref_inner_prod_list, ref_inner_prod_error_list = curvefit.get_inner_product(b_ref_star_list)
    # choose the standard for checking two stars is the same.
    star_list_length = len(inner_prod_list)
    if VERBOSE>1 : print "length_inner_prod = ", star_list_length
    ref_star_list_length = len(ref_inner_prod_list)
    if VERBOSE>1 : print "length_ref_inner_prod = ", ref_star_list_length
    if star_list_length < ref_star_list_length:
        threshold = (star_list_length - 1)*(star_list_length - 2)* 0.60 /2.0
    elif ref_star_list_length <= star_list_length:
        threshold = (ref_star_list_length - 1)*(ref_star_list_length - 2) * 0.60/2.0
    if VERBOSE>1 : print 'threshold = ', threshold
    # do match 
    for i in xrange(len(ref_inner_prod_list)):
        relation_count = np.array([])
        for j in xrange(len(inner_prod_list)):
            temp = curvefit.relation_counter(ref_inner_prod_list[i], inner_prod_list[j], inner_prod_error_list[j])
            relation_count = np.append(relation_count, temp)
        # determind which one is the most relative
        relation_max = np.amax(relation_count)
        if VERBOSE>1 : print relation_count
        index_relation_max = np.argmax(relation_count)
        if relation_max > threshold:
            # form a vector of ref star position and match star position, then send to the match_star_list
            match_star = np.array([ref_star_list[i][1],ref_star_list[i][2], star_list[index_relation_max][1], star_list[index_relation_max][2]])
            match_star_list.append(match_star)
            delta_x = match_star[2] - match_star[0]
            delta_x_list = np.append(delta_x_list, delta_x)
            delta_y = match_star[3] - match_star[1]
            delta_y_list = np.append(delta_y_list, delta_y)
            if VERBOSE>2 : print "match: ",match_star, "delta_x = ", delta_x ,"delta_y = ", delta_y

    if len(match_star_list) < 3:
        print "No enough matched stars, match failed."
        return False, False, False, False

    return match_star_list, delta_x_list, delta_y_list, True

def get_img_property(VERBOSE = 0):
    path = os.getcwd()
    list_path = path.split("/")
    scope_name = list_path[-5]
    date_name = list_path[-3]
    obj_name = list_path[-2]
    filter_name = list_path[-1]
    return scope_name, date_name, obj_name, filter_name

def get_significant_stars(data, peak_list, hwl = 4, ecc =1, VERBOSE = 0):
    #-------------------------------------
    # find stars from peaks
    star_list = curvefit.get_star(data, peak_list, margin = 4, half_width_lmt = hwl, eccentricity = ecc)
    # the order is set in curvefit.get_star
    star_list = np.sort(star_list, order = 'amplitude')
    # Choose 20 the most bright stars as the reference.
    if len(star_list) > 20 :
        star_list = star_list[-20:]
    if VERBOSE>1:print "hwl = {0}, len of star_list = {1}".format(hwl, len(star_list))
    if VERBOSE>3:
        print "star list: "
        for star in star_list:
            print star[2], star[1]
    star_list = np.sort(star_list, order = 'xsigma')
    star_list = np.sort(star_list, order = 'ysigma')
    if VERBOSE>1 :
        print "The number of star is ", len(star_list)
        for value in star_list:
            print "height = ", value[0], " position= (", value[1], value[2], ") size= (", value[3], value[4],")"    
    return star_list

def plot_dots(data, data_mean, data_std, peak_list, star_list):
    # draw three plot, one with point, another without
    f = plt.figure(fits_list[order])
    plt.imshow(data, vmin = data_mean - 1 * data_std , vmax = data_mean + 1 * data_std )
    plt.colorbar()
    f.show()

    g = plt.figure(fits_list[order]+'_peaks')
    plt.imshow(data, vmin = data_mean - 1 * data_std , vmax = data_mean + 1 * data_std )
    plt.colorbar()
    for pos in peak_list:
        plt.plot( pos[1], pos[0] , 'ro')
    g.show()

    h = plt.figure(fits_list[order]+'_stars')
    plt.imshow(data, vmin = data_mean - 1 * data_std , vmax = data_mean + 1 * data_std )
    plt.colorbar()
    for pos in star_list:
        plt.plot( pos[2], pos[1] , 'ro')
    h.show()
    raw_input()
    return
#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 3
    # measure times
    start_time = time.time()
    # get all names of fits
    list_name=argv[-1]
    fits_list=tat_datactrl.readfile(list_name)
    #----------------------------------------------------------------------
    #main code
    # get the data of referance img.
    # include mean, std, the position of stars.
    scope_name, date_name, obj_name, filter_name = get_img_property()
    path_of_result = tat_datactrl.get_path("path_of_result")
    ref_name ="{2}/reference/{1}_{0}.fits".format(date_name[:-4], obj_name, path_of_result)
    if VERBOSE>1 :
            print " "
            print "--- ", ref_name, " ---"
    try:
        ref_data = pyfits.getdata(ref_name+"pass")
    except:
        ref_name = fits_list[0]
        del fits_list[0]
        if VERBOSE>1:
            print "No reference, use the first image as reference."
            print " "
            print "--- ", ref_name, " ---"
        ref_data = pyfits.getdata(ref_name)
    ref_paras, ref_cov = curvefit.hist_gaussian_fitting("default", ref_data)
    ref_data_mean = ref_paras[0]
    ref_data_std = ref_paras[1]
    if VERBOSE>1:
        print "mean: ", ref_data_mean, "std: ", ref_data_std
    # test hwo many peak in this figure.
    # If too much, raise up the limitation of size
    sz = 29
    tl = 15
    ref_peak_list = []
    while len(ref_peak_list) >500 or len(ref_peak_list) < 3:
        sz +=1
        ref_peak_list = curvefit.get_peak_filter(ref_data, tall_limit = tl, size = sz)
    if VERBOSE>3:
        print "peak list: "
        for peak in ref_peak_list:
            print peak[1], peak[0]
    ref_star_list = get_significant_stars(ref_data, ref_peak_list, hwl = 4, ecc =1, VERBOSE = 3)
    if VERBOSE>3:
        plot_dots(ref_data, ref_data_mean, ref_data_std, ref_peak_list, ref_star_list)

    # matching images
    for order in xrange(len(fits_list)):
        if VERBOSE>1 :
            print " "
            print "--- {0} ---".format(fits_list[order])
        data = pyfits.getdata(fits_list[order])
        paras, cov = curvefit.hist_gaussian_fitting("default", data)
        data_mean = paras[0]
        data_std = paras[1]
        if VERBOSE>1:
            print "mean: ", data_mean, "std: ", data_std
        # rest sz and hwl, because ref img is clear, easy to find stars, but belows is not.
        peak_list = curvefit.get_peak_filter(data, tall_limit = tl, size = sz) 
        star_list = get_significant_stars(data, peak_list, hwl = 4, ecc = 1, VERBOSE = 3)
        if len(star_list) < 3:
            print fits_list[order], "Number of stars is less than 3, match fail."
            continue
        # Visualize the result
        if VERBOSE>3:
            plot_dots(data, data_mean, data_std, peak_list, star_list)
        # match function call    
        match_star_list, delta_x_list, delta_y_list, succeed = get_match(ref_star_list, star_list )    
        if not succeed:
            continue 
        # if std of delta is larger than 1, delete the exotic one value until std of delta less than 1.
        delta_x_list = curvefit.get_rid_of_exotic_severe(delta_x_list)
        mean_delta_x = np.mean(delta_x_list)
        std_delta_x = np.std(delta_x_list)
        # if std of delta is larger than 1, delete the exotic one value until std of delta less than 1.
        delta_y_list = curvefit.get_rid_of_exotic_severe(delta_y_list)
        mean_delta_y = np.mean(delta_y_list)
        std_delta_y = np.std(delta_y_list)
        if len(delta_x_list) < 3 or len(delta_y_list) < 3:
            print fits_list[order], "Number of stars is less than 3, match fail."
            continue
        if VERBOSE>1 :
            print "the result of match"
            print "mean of delta_x: ", mean_delta_x ," stdev = ", std_delta_x
            print "mean of delta_y: ", mean_delta_y ," stdev = ", std_delta_y
        create_matched_fits(fits_list[order], data, mean_delta_x, mean_delta_y)
        if VERBOSE>0 : print fits_list[order], "match OK"

        elapsed_time = time.time() - start_time
        if VERBOSE>1 : print "Exiting Main Program, spending ", elapsed_time, "seconds."
    
    # measuring time
    elapsed_time = time.time() - start_time
    if VERBOSE>0 : print "Exiting Main Program, spending ", elapsed_time, "seconds."
