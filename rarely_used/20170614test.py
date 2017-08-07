#!/usr/bin/python

import numpy as np
import scipy.ndimage.filters as filters

# calculate the inner product of two side, from star_1 to star_2 and from star_1 to star_3.
def inner_product(star_1, star_2, star_3):
    inner_prod = (star_1[1] - star_2[1])*(star_1[1] - star_3[1]) + (star_1[2] - star_2[2])*(star_1[2] - star_3[2])
    return inner_prod

# choose a star as a target, than choose two else the calculate the inner product.
def get_inner_product(star_list):
    inner_prod_star_list = []
    # choose a star, named A
    for i in xrange(len(star_list)):
        inner_prod_star = np.array([])
        # choose two else stars, named B and C, to get inner product of two side AB and AC.
        for j in xrange(len(star_list)):
            if i == j:
                continue
            for k in xrange(len(star_list)):
                if k == i:
                    continue
                if k <= j:
                    continue
                print star_list[i], star_list[j], star_list[k]
                inner_prod = inner_product(star_list[i], star_list[j], star_list[k])
                print inner_prod
                inner_prod_star = np.append(inner_prod_star, inner_prod)
        inner_prod_star_list.append(inner_prod_star)
    inner_prod_star_list = np.array(inner_prod_star_list)
    return inner_prod_star_list

A = np.array([1., 0., 0.])
B = np.array([1., 2., 2.])
C = np.array([1., 2., -3.])
D = np.array([1., -2., -2.])
star_list = np.array([A, B, C, D])
ans = get_inner_product(star_list)
print ans
