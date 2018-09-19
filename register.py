#!/usr/bin/python
'''
Program:
    This is a program for registering psf on images. 
Usage: 
    register.py [list of names of images]
Editor:
    Jacob975
20170628
#################################
update log
20180628 version alpha 1
    1. The code works
'''
from astropy.io import fits as pyfits
import numpy as np
import time
from sys import argv
from register_lib import get_inner_product, num_relation_lister, get_rid_of_exotic, get_rid_of_exotic_severe
from starfinder import starfinder
import os

class register:
    def __init__(self, iraf_table, infos):
        print "register initialization star"
        self.ref_infos = infos
        # Completness check
        if len(iraf_table) < 3:
            print "Too few stars for registration in {0}".format(infos.name_image)
            return 1, 0, 0
        # Don't take sources near the edge of images. 
        iraf_table = iraf_table[np.argsort(iraf_table[:, -2])]
        iraf_table = iraf_table[(iraf_table[:,1] > 50) & (iraf_table[:,1] < 980)]
        iraf_table = iraf_table[(iraf_table[:,2] > 50) & (iraf_table[:,2] < 980)]
        # Take first 10 only
        try:
            iraf_table = iraf_table[-10:]
            print "Pick 10 first star only from {0}".format(infos.name_image)
        except:
            print "Warning, The number of source is less than 10 in this image"
        print iraf_table[:, 1:3]
        self.ref_iraf_table = iraf_table
        self.ref_inner_prod_list, self.ref_inner_prod_error_list = get_inner_product(iraf_table, infos)
        print "register initialization done"
        return
    def offset(self, iraf_table, infos):
        # Load ref
        ref_iraf_table = self.ref_iraf_table
        ref_inner_prod_list = self.ref_inner_prod_list
        ref_infos = self.ref_infos
        # Completness check
        if len(iraf_table) < 3:
            print "Too few stars for registration in {0}".format(infos.name_image)
            return 1, 0, 0
        # Take first 10 only
        iraf_table = iraf_table[np.argsort(iraf_table[:, -2])]
        iraf_table = iraf_table[(iraf_table[:,1] > 50) & (iraf_table[:,1] < 980)]
        iraf_table = iraf_table[(iraf_table[:,2] > 50) & (iraf_table[:,2] < 980)]
        try:
            iraf_table = iraf_table[-10:]
            print "Pick 10 first star only from {0}".format(infos.name_image)
        except:
            print "Warning, The number of source is less than 10 in this image"
        print iraf_table[:, 1:3]
        #-----------------------------------------------
        # Calculate inner prod.
        inner_prod_list, inner_prod_error_list = get_inner_product(iraf_table, infos)
        # Threshold of match inner products
        star_list_length = len(inner_prod_list)
        ref_iraf_table_length = len(ref_inner_prod_list)
        if star_list_length < ref_iraf_table_length:
            threshold = (star_list_length - 1)*(star_list_length - 2)* 0.60 /2.0
        elif ref_iraf_table_length <= star_list_length:
            threshold = (ref_iraf_table_length - 1)*(ref_iraf_table_length - 2) * 0.60/2.0
        print "threshold: {0}".format(threshold)
        #------------------------------------------------
        # Registrate
        offset_xs = np.array([])
        offset_ys = np.array([])
        match_table = []
        print "--- num of match innor product ---"
        for i in xrange(len(ref_inner_prod_list)):
            num_relation_list = []
            for j in xrange(len(inner_prod_list)):
                num_relation = num_relation_lister(ref_inner_prod_list[i], inner_prod_list[j], inner_prod_error_list[j])
                num_relation_list.append(num_relation)
            # determind which one is the most relative
            print num_relation_list
            num_relation_max = np.amax(num_relation_list)
            index_num_relation_max = np.argmax(num_relation_list)
            if num_relation_max > threshold:
                # form a vector of ref star position and match star position, then send to the match_star_list
                match_star = np.array([ref_iraf_table[i][1], ref_iraf_table[i][2], iraf_table[index_num_relation_max][1], iraf_table[index_num_relation_max][2]])
                match_table.append(match_star)
                offset_x = match_star[2] - match_star[0]
                offset_xs = np.append(offset_xs, offset_x)
                offset_y = match_star[3] - match_star[1]
                offset_ys = np.append(offset_ys, offset_y)
                print "match star: {0}, offset_x = {1}, offset_y = {2}".format(match_star, offset_x, offset_y)
        if len(offset_xs) < 3 or len(offset_ys) < 3:
            print "No enough match stars"
            return 1, 0, 0
        # Wipe out non-sense offset
        offset_xs = get_rid_of_exotic_severe(offset_xs)
        offset_ys = get_rid_of_exotic_severe(offset_ys)
        if len(offset_xs) < 3 or len(offset_ys) < 3:
            print "No enough match stars"
            return 1, 0, 0
        offset_xm = np.median(offset_xs)
        offset_ym = np.median(offset_ys)
        print "--- offset_xm = {0}, offset_ym = {1}".format(offset_xm, offset_ym)
        return 0, offset_xm, offset_ym

def shift_image(name_image, offset_x, offset_y):
    data = pyfits.getdata(name_image)
    imAh = pyfits.getheader(name_image)
    rotation_matrix_inverse = np.array([[1, 0, offset_x],[0, 1, offset_y],[0,0,1]], dtype = float)
    regrided_data = regrid_data(data, rotation_matrix_inverse)
    pyfits.writeto(name_image[0:-5]+'_m.fits', regrided_data, imAh, overwrite = True)
    return

def regrid_data(data, rotation_matrix_inverse ):
    # construct the translation matrix of two fits
    regrided_data = np.empty(data.shape) 
    pre_coor = np.array([500.0, 500.0, 1.0])
    new_coor = np.dot(rotation_matrix_inverse, pre_coor)
    area = np.array([(1-new_coor[0]%1) * (1-new_coor[1]%1), (new_coor[0]%1) * (1-new_coor[1]%1), (new_coor[0]%1) * (new_coor[1]%1), (1-new_coor[0]%1) * (new_coor[1]%1)])
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
    return regrided_data

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #---------------------------------------
    # Load arguments and Initialize
    if len(argv) != 2:
        print "Error! Wrong arguments"
        print "Usage: register.py [list of names of images]"
        exit(1)
    list_name = argv[1]
    #---------------------------------------
    # Load data
    try:
        image_list=np.loadtxt(list_name, dtype = str)
    except:
        print "Wrong list of names of images"
        exit(1)
    # Pick one as reference image
    print "--- ref: {0} ---".format(image_list[len(image_list)/2])
    ref_iraf_table, ref_infos = starfinder(image_list[len(image_list)/2])
    print "number of found stars: {0}\nsigma = {1}".format(len(ref_iraf_table), ref_infos.sigma)
    ref_iraf_table = np.array([x for t in ref_iraf_table for x in t]) 
    ref_iraf_table = np.reshape(ref_iraf_table, (-1, 12))
    find_offset = register(ref_iraf_table, ref_infos)
    # Register
    for i in xrange(len(image_list)):
        print "--- {0} ---".format(image_list[i])
        iraf_table, infos = starfinder(image_list[i])
        print "number of found stars: {0}\nsigma = {1}".format(len(iraf_table), infos.sigma)
        iraf_table = np.array([x for t in iraf_table for x in t]) 
        iraf_table = np.reshape(iraf_table, (-1, 12))
        failure, offset_xm, offset_ym = find_offset.offset(np.array(iraf_table), infos)
        # if registration is OK, save the shifted image
        if not failure:
            shift_image(image_list[i], offset_ym, offset_xm)
            print "{0}_m.fits, OK".format(image_list[i][:-5])
    os.system("ls *_m.fits > registed_image_list.txt")
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
