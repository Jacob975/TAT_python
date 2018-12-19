#!/usr/bin/python
'''
Program:
    This is a liberary program of register 
Usage:
    1. from register_lib import [func name] or import curvefit
    2. use it in your lovely code.
Editor:
    Jacob975
#################################
update log
20180628 version alpha 1
    1. Remove some 
'''
import numpy as np

# calculate the inner product and error of two side, from star_1 to star_2 and from star_1 to star_3.
def inner_product(star_1, star_2, star_3, sigma):
    try:
        inner_prod = (star_2[0] - star_1[0])*(star_3[0] - star_1[0]) + (star_2[1] - star_1[1])*(star_3[1] - star_1[1])
        x_part_1 = np.power(star_1[0] - star_2[0], 2)
        x_error_1 = (2 * np.power(sigma, 2))/x_part_1
        x_part_2 = np.power(star_1[0] - star_3[0], 2)
        x_error_2 = (2 * np.power(sigma, 2))/x_part_2
        y_part_1 = np.power(star_1[1] - star_2[1], 2)
        y_error_1 = (2 * np.power(sigma, 2))/y_part_1
        y_part_2 = np.power(star_1[1] - star_3[1], 2)
        y_error_2 = (2 * np.power(sigma, 2))/y_part_2
        var = x_part_1*x_part_2*(x_error_1 + x_error_2) + y_part_1*y_part_2*(y_error_1 + y_error_2)
        error = np.power(var, 0.5)
    except : 
        return 0, 0
    else:
        return inner_prod, error

# check the number of matching inner prod of two stars, then return the number.
def num_relation_lister(ref_star, star, error):
    
    valid_inner_prod = 0
    for ref_inner_prod in ref_star:
        for i in xrange(len(star)):
            if ref_inner_prod <= star[i] + error[i] and ref_inner_prod >= star[i] - error[i]:
                valid_inner_prod = valid_inner_prod + 1
                continue
    return valid_inner_prod

# choose a star as a target, than choose two else the calculate the inner product.
def get_inner_product(iraf_table, infos = None):
    inner_prod_star_list = []
    inner_prod_error_list = []
    sigma = 2.0
    # choose a star, named A
    for i in xrange(len(iraf_table)):
        inner_prod_star = np.array([])
        inner_prod_error = np.array([])
        # choose two else stars, named B and C, to get inner product of two side AB and AC.
        for j in xrange(len(iraf_table)):
            if i == j:
                continue
            for k in xrange(len(iraf_table)):
                if k == i:
                    continue
                if k <= j:
                    continue
                inner_prod, error = inner_product(iraf_table[i,1:3], iraf_table[j,1:3], iraf_table[k,1:3], sigma)
                inner_prod_star = np.append(inner_prod_star, inner_prod)
                inner_prod_error = np.append(inner_prod_error, error)
        # set all inner product as a list, seems like DNA of this star
        inner_prod_star_list.append(inner_prod_star)
        inner_prod_error_list.append(inner_prod_error)
    inner_prod_star_list = np.array(inner_prod_star_list)
    inner_prod_error_list = np.array(inner_prod_error_list)
    return inner_prod_star_list, inner_prod_error_list

# choose a star as a target, than choose two else the calculate the inner product.
def get_inner_product_SE(SE_table):
    inner_prod_star_list = []
    inner_prod_error_list = []
    sigma = 2.0
    # choose a star, named A
    for i in xrange(len(SE_table)):
        inner_prod_star = np.array([])
        inner_prod_error = np.array([])
        # choose two else stars, named B and C, to get inner product of two side AB and AC.
        for j in xrange(len(SE_table)):
            if i == j:
                continue
            for k in xrange(len(SE_table)):
                if k == i:
                    continue
                if k <= j:
                    continue
                inner_prod, error = inner_product(SE_table[i,2:4], SE_table[j,2:4], SE_table[k,2:4], sigma)
                inner_prod_star = np.append(inner_prod_star, inner_prod)
                inner_prod_error = np.append(inner_prod_error, error)
        # set all inner product as a list, seems like DNA of this star
        inner_prod_star_list.append(inner_prod_star)
        inner_prod_error_list.append(inner_prod_error)
    inner_prod_star_list = np.array(inner_prod_star_list)
    inner_prod_error_list = np.array(inner_prod_error_list)
    return inner_prod_star_list, inner_prod_error_list

#--------------------------------------------------------------------
# This is a func to wipe out exotic number in a list
# This one is made for matching images
def get_rid_of_exotic_severe(value_list, VERBOSE = 0):
    answer_value_list = value_list[:]
    std = np.std(answer_value_list)
    # resursive condition
    while std > 1 :
        mean = np.mean(answer_value_list)
        # get the error of each value to the mean, than delete one with largest error.
        sub_value_list = np.subtract(answer_value_list, mean)
        abs_value_list = np.absolute(sub_value_list)
        index_max = np.argmax(abs_value_list)
        answer_value_list= np.delete(answer_value_list, index_max)
        std = np.std(answer_value_list)
    return answer_value_list

# This one is made for scif calculation
def get_rid_of_exotic(value_list):
    std = np.std(value_list)
    mean = np.mean(value_list)
    # get the error of each value to the mean, than delete one with largest error.
    sub_value_list = np.subtract(value_list, mean)
    abs_value_list = np.absolute(sub_value_list)
    for i in xrange(len(abs_value_list)):
        if abs_value_list[i] >= 3 * std:
            value_list = np.delete(value_list, i)
            value_list = get_rid_of_exotic(value_list)
            return value_list
    return value_list
