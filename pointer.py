#!/usr/bin/python
'''
Program:
This is a program to direct the position of the coordinate on image.. 
It should be only used as a library.
Classes included:
    1. pointer
    2. ccs (celectial coordinate system)

Test Usage:
1. pointer.py

editor Jacob975
20171210
#################################
update log

20171210 version alpha 1
    1. class of celectial coordinate system is partically done(init, self correction, add) 
    2. class of pointer haven't been done, this is used to find the right name of image of the star belonging to.
'''
from sys import argv
import numpy as np
import pyfits
import time
import TAT_env

#  this class is uesd to direct the position of the coordinate on image.
class pointer:
    object_list = TAT_env.object_list
    RA = None
    DEC = None
    rlt_img = None
    def __init__(self, RA, DEC):
        self.RA = ccs(RA)
        self.DEC = ccs(DEC)
        self.near_obj, self.rlt_img = self.finder(self.RA, self.DEC)
        if VERBOSE>1: self.ds9()
        return

    def finder(self, RA, DEC):
        # determine the coordinate is on the image or not.
        for obj in self.object_list:
            obj_RA = self.read(obj['RA'])
            obj_DEC = self.read(obj['DEC'])
            ans = self.match(obj_RA, obj_DEC, RA, DEC)
            # if True, return the name of main object on the iamge and the ref name of the image.
        return near_obj, rlt_img
    def match(self, ref_RA, ref_DEC, tar_RA, tar_DEC):
        pass
        return
    def ds9(self):
        return

# celectial coordinate system
class ccs:
    hms = None
    dms = None
    def __init__(self, hms, dms):
        if type(hms) == str:
            self.hms = self.read(hms)
        else:
            self.hms = hms
        if type(dms) == str:
            self.dms = self.read(dms)
        else:
            self.dms = dms
        hms = self.check_valid_hms(self.hms)
        dms = self.check_valid_dms(self.dms)
        return
    # read hms or dms from str
    def read(self, coord):
        coord_list = coord.split(":")
        coord_list = map(int, coord_list)
        return coord_list
    # check the vality fo hms recusively.
    def check_valid_hms(self, inp):
        ans = inp[:]
        for i in xrange(len(ans)):
            if i == 0:
                if ans[i] < 0.0:
                    ans[i] += 24.0
                    continue
                if ans[i] >= 24.0:
                    ans[i] -= 24.0
                    continue
            else :
                if ans[i] <0.0:
                    ans[i-1] -= 1.0
                    ans[i] += 60.0
                    continue
                if ans[i] >= 60.0:
                    ans[i-1] += 1.0
                    ans[i] -= 60
                    continue
        if ans[0] == inp[0] and ans[1] == inp[1]:
            return ans
        else:
            return self.check_valid_hms(ans)
    # add two hms into one
    def add_hms(self, A_hms, B_hms):
        ans = [0.0 for i in xrange(len(A_hms))]
        for i in xrange(len(ans)):
            ans[i] = A_hms[i] + B_hms[i]
        ans = self.check_valid_hms(ans)
        return ans
    # check the vality fo hms recusively.
    def check_valid_dms(self, inp):
        ans = inp[:]
        for i in xrange(len(ans)):
            if i == 0:
                if ans[i] < -90.0 or ans[i] > 90.0:
                    print "invalid dms"
                    return None
            else :
                if ans[i] <0.0:
                    ans[i-1] -= 1.0
                    ans[i] += 60.0
                    continue
                if ans[i] >= 60.0:
                    ans[i-1] += 1.0
                    ans[i] -= 60
                    continue
        if ans[0] == inp[0] and ans[1] == inp[1]:
            return ans
        else:
            return self.check_valid_dms(ans)
    # add two dms into one
    def add_dms(self, A_dms, B_dms):
        ans = [0.0 for i in xrange(len(A_dms))]
        for i in xrange(len(ans)):
            ans[i] = A_dms[i] + B_dms[i]
        ans = self.check_valid_dms(ans)
        return ans
                
    def __add__(self, A):
        ans_hms = self.add_hms(self.hms, A.hms)
        ans_dms = self.add_dms(self.dms, A.dms)
        return ccs(ans_hms, ans_dms)
    def __str__(self):
        line1 = "hms = {0:.2f}:{1:.2f}:{2:.2f}\n".format(self.hms[0], self.hms[1], self.hms[2])
        line2 = "dms = {0:.2f}:{1:.2f}:{2:.2f}".format(self.dms[0], self.dms[1], self.dms[2])
        return line1+line2

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # -----------------------------------
    # this part is uesd to check class ccs working.
    stu1 = ccs('25:00:61', '00:00:61')
    print "stu1: \n{0}".format(stu1)
    stu2 = ccs('00:59:00', '00:59:00')
    print "stu2: \n{0}".format(stu2)
    stu3 = stu1 + stu2
    print "stu3: \n{0}".format(stu3)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
