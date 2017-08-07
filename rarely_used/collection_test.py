#!/usr/bin/python

import os
import numpy as np
import matplotlib.pyplot as plt
from numpy import pi, r_

def get_noise(fits_list):
    answer = ""
    for name in fits_list:
        answer += name
    return answer

def collection( obj_list, k_factor, noise_list, answer_list = []):
    if k_factor == 0:
        #print answer_list
        noise = get_noise(answer_list)
        noise_list.append(noise)
        return
    for i in xrange(len(obj_list)):
        sub_answer_list = answer_list[:]
        sub_answer_list.append(obj_list[i])
        sub_obj_list = obj_list[i+1:]
        collection(sub_obj_list, k_factor - 1, noise_list, sub_answer_list)
    return
name_list = ['A','B','C','D','E']
noise_list = []
for i in xrange(len(name_list)):
    collection(name_list, i, noise_list)

for noise in noise_list:
    print noise
