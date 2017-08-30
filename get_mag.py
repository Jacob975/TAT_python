#!/usr/bin/python
'''
Program:
This is a program to demo the style of my code. 
Usage:
1. get_mag.py [eccentricity] [band] [fits name]

eccentricity
    This is a option to limit the eccentricity of local found star catalog
    from 0 to 1 is proper, over this range will disable this limitation.
    default : 0.9

band
    This is a option, controlling which kind of database will be drop.
    It is a option with default value: "N".

fits name
    You should put a fits name over there.
    and this fit should come with wcs coord.
    method will be set by the hint in fits name

e.g $get_mag.py Median_mdn_w.fits       # method will be set as 'mdn'
    $get_mag.py V Median_mdn_w.fits     # method will be set as 'mdn', band will be set as V band
    $get_mag.py 1 N Median_mdn_w.fits   # method will be set as 'mdn', band will be set as N band, 
                                          tolerated eccentricity of stars will be set as 1
editor Jacob975
20170710
#################################
update log
    20170710 version alpha 1
        This code can run properly.

    20170711 version alpha 2
        1. This code will save data in /home/Jacob975/demo/20170605_meeting/delta_mag.tsv
            details is writen in header.
        2. Now you can not only put in file to generate result but also put in fits
            details is writen in header.

    20170717 version alpha 3
        1.  When calculating the delta magnitude, It will do error transmission from ref data.
            not just take the standard deviation of stars' magnitude.
        2.  So on the error of instrument magnitude is not been measured by gaussian 2D fitting,
            we just skip it until well done.

    20170718 version alpha 4 
        1.  Rolling back the change of alpha 3
            Base on statistic, when findding the stdev for a lot of data with error.
            We should do statistic by weight, which is controlled by error.
            not just pass the error of themself.

            try to think about a question, A and B are value.
            A = 100 +- 0.1
            B = 0 +- 0.1
            what is their stdev?
            I'm pretty sure that is not 0.141, It should be much greater.

            So on I don't statistic by weight, because the structure of math haven't be constructed.
        2.  now you cannot use this code with only local catalog and ref catalog
            you can only using the fits with wcs and band letter.
        3.  add a new option ecc to limit the eccentricity of local found star catalog.

    20170718 version alpha 5
        1.  add the ability to process band U, B, V, R, I.
    
    20170728 version alpha 6
        1.  Update the func of error magnitude, now it will be generate by weighted average and stdev.
        2.  fix some bugs about nan. or inf. come into calculation.

    20170808 version alpha 7
        1.  use tat_config to control path of result data instead of fix the path in the code.

    20170829 version alpha 8
        1.  set the source code classified completely
        2.  use fits as save datatype instead of tsv.
'''
from sys import argv, exit
import numpy as np
import pyfits
import time
import curvefit
import os
import math
import tat_datactrl
import glob
from astropy.table import Table

# This is a code to add several stars, and then find out the equivelent magnitude.
def get_add_mag(matched_array, band):
    mag_array = []
    # for different band, the position of mag is different.
    if band == "N":
        mag_array = np.array(matched_array[:,6], dtype = float)
    elif band == "U":
        mag_array = np.array(matched_array[:,11], dtype = float)
    elif band == "B":
        mag_array = np.array(matched_array[:,7], dtype = float)
    elif band == "V":
        mag_array = np.array(matched_array[:,8], dtype = float)
    elif band == "R":
        mag_array = np.array(matched_array[:,6], dtype = float)
    elif band == "I":
        mag_array = np.array(matched_array[:,9], dtype = float)
    count_array = curvefit.mag2count(mag_array)
    count = np.sum(count_array)
    mag = curvefit.count2mag(count)
    return mag

# This is a code to mean several delta_m, and then find out the equivelent magnitude.
def weighted_avg_and_std(values, weights):
    #Return the weighted average and standard deviation.
    #values, weights -- Numpy ndarrays with the same shape.
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)  # Fast and numerically precise
    return average, math.sqrt(variance)

# get property of images from path
def get_img_property(image_name):
    image_name_list = image_name.split("_")
    try: 
        scope_name = image_name_list[0]
        date_name = image_name_list[1]
        obj_name = image_name_list[2]
        filter_name = "{0}_{1}".format(image_name_list[3], image_name_list[4])
    except:
        print "Inproper name, get property changing ot dir"
        path = os.getcwd()
        list_path = path.split("/")
        scope_name = list_path[-5]
        date_name = list_path[-3]
        obj_name = list_path[-2]
        filter_name = list_path[-1]
    method = image_name_list[-2]
    return scope_name, date_name, obj_name, filter_name, method

#-----------------------------------------------------
# This class is for control argument from outside.
class argv_ctrl:
    argument = []
    fn = ""
    e = 1.0
    b = "N"
    # initialized with argument from sys.argv
    def __init__(self, argument):
        self.argument = argument
        # check the number of argument is valid.
        if len(argument) < 2:
            print "No argument"
            print "Usage: get_mag.py [eccentricity] [band] [list name]"
            return
        elif len(argument) > 4:
            print "Too many argument"
            print "Usage: get_mag.py [eccentricity] [band] [list name]"
            return
        # distribute value into proper position.
        for i in xrange(len(argument)):
            if i == 0:
                continue
            elif i == len(argument) - 1:
                self.fn = argument[i]
                continue
            try: float(argument[i])
            except: pass
            else: self.e = argument[i]

            try: str(argument[i])
            except: pass
            else: self.b = argument[i]
    # for return value
    def fits_name(self):
        return self.fn
    def ecc(self):
        return self.e
    def band(self):
        return self.b

#--------------------------------------------
# The class is for control procession of data
class main_process:
    fits_name = ""              # fits name.
    band = ""                   # the band we used for take picture.
    ecc = 0.0                   # the limitation of tolerated eccentricity.
    ref_table = 0               # the ref star catalog in table datatype.
    local_table = 0             # the local star catalog in table datatype.
    result_delta_m = 0.0        # the delta magnitude.
    result_delta_std = 0.0      # the error of delta magnitude.
    result = []                 # the data will be writen in files.
    def __init__(self, fits_name, band, ecc):
        # save txt
        self.fits_name = fits_name
        self.band = band
        self.ecc = ecc
        # grab both refs and locals
        self.ref_table = self.get_ref()
        self.local_table = self.get_local()
        # Match
        self.result_delta_m, self.result_delta_std = self.match_star()
        self.save()
        return
    def get_ref(self):          # <- debug here, lots of bugs about path
        # grab ref_star_catalog from [path_of_result]/ref_catalog
        # If no ref_star_catalog, The code will download proper ref_star_catalog.
        #--------
        # get property of images from current path
        scope_name, date_name, obj_name, filter_name, method = get_img_property(self.fits_name)
        ref_name = "{0}_{1}_{2}.tsv".format(scope_name, obj_name, self.band)
        path_of_result = tat_datactrl.get_path("path_of_result")
        path_of_ref = "{0}/ref_catalog".format(path_of_result)      # the ref catalog pool
        # check the existance of ref
        ref_name_list = glob.glob("{0}/*.tsv".format(path_of_ref))
        try :
            ref_index = ref_name_list.index("{0}/{1}".format(path_of_ref, ref_name))
        except:
            if VERBOSE>0: print "No reference, automatically download reference by ds9."
            os.system("get_w_stls.py {1} {0}".format(self.fits_name, self.band))
            temp = "cp {0} {1}/{0}".format(ref_name, path_of_ref)
            os.system(temp)
        # read refs
        ref_catalog = tat_datactrl.read_tsv_file("{0}/{1}".format(path_of_ref, ref_name))
        ref_table = self.arr2table(ref_catalog, 1)
        return ref_table
    # this def is for convert arr like data into table
    # Because ds9 always return tsv datatype.
    def arr2table(self, arr, start_point):
        # start_point mean where is the start of data
        ans = Table(rows = arr[start_point:], names = np.array(arr[0]))
        if start_point == 2:
            for i in xrange(len(arr[0])):
                ans[arr[0][i]].unit = arr[1][i]
        return ans
    def get_local(self):
        # This code will grab star_catalog( bright star only) by get_info.
        local_name = "{0}_stls.fits".format(self.fits_name[:-5])
        os.system("get_info.py {1} {0}".format(self.fits_name, self.ecc))
        local_table = Table.read(local_name)
        return local_table
    def match_star(self):
        # match stars in refs and locals.
        # If matched save them in a table.
        seperation = 0.001
        local_table = self.local_table
        ref_table = self.ref_table 
        delta_m_list = []
        e_delta_m_list = []
        for i in xrange(len(local_table)):
            matched_list = []
            local_mag = float(local_table[i]['mag'])
            for j in xrange(len(ref_table)):
                _RA = float(ref_table[j]['_RAJ2000'])
                RA = float(local_table[i]['RAJ2000'])
                _DEC = float(ref_table[j]['_DEJ2000'])
                DEC = float(local_table[i]['DECJ2000'])
                # because the resolution of telescope, we tolerate a range for matching stars.
                the_same_RA = bool(RA - seperation < _RA and RA + seperation > _RA )
                the_same_DEC = bool(DEC - seperation < _DEC and DEC + seperation > _DEC)
                if the_same_RA and the_same_DEC:
                    matched_list.append(list(ref_table[j]))
                    if VERBOSE>1:
                        print "Belows are the same"
                        print "local_pos: {0}, {1}".format(RA, DEC)
                        print "ref_pos: {0}, {1}".format(_RA, _DEC)
                        print "mag = {0}+-{1}".format(local_table[i]['mag'], local_table[i]['e_mag'])
                        print "Ref_mag = "+ref_table.columns[6][j]
            # Test how many star in the ref is match to the local
            # If more than 1, the count will add together.
            if len(matched_list) == 0:
                print "no matched star"
                continue
            matched_list = np.array(matched_list)
            ref_mag = get_add_mag(matched_list, self.band)
            delta_mag = ref_mag - local_mag
            e_mag = float(local_table[i]['e_mag'])
            if np.isnan(e_mag) or np.isinf(e_mag):
                continue
            if np.isnan(delta_mag) or np.isinf(delta_mag):
                continue
            delta_m_list.append(delta_mag)
            e_delta_m_list.append(e_mag)
            if VERBOSE>0:
                print "ref_mag: {0:.2f}, local_mag: {1:.2f}+-{3:.2f}, delta: {2:.2f}+-{3:.2f}".format(ref_mag, local_mag, delta_mag, e_mag)
        # calculate the delta of magnitude.
        delta_m_list = np.array(delta_m_list)
        e_delta_m_list = np.array(e_delta_m_list)
        delta_m_list, e_delta_m_list = curvefit.get_rid_of_exotic_vector(delta_m_list, e_delta_m_list)
        result_delta_m, result_delta_std = weighted_avg_and_std(delta_m_list, e_delta_m_list)
        result_delta_m = round(result_delta_m, 2)
        result_delta_std = round(result_delta_std, 2)
        if VERBOSE>0:print "In average, delta_mag = {0:.2f}+-{1:.2f}".format(result_delta_m, result_delta_std)
        return result_delta_m, result_delta_std
    # This def is for generate the line will be writen in files.
    def set_result(self):
        scope_name, date_name, obj_name, filter_name, method = get_img_property(self.fits_name)
        if float(self.ecc) > 0 and float(self.ecc) < 1:
            writen_ecc = ecc
        else:
            writen_ecc = "N"
        result = [self.result_delta_m, self.result_delta_std, obj_name, scope_name, filter_name, date_name, method, self.band, writen_ecc]
        return result
    # This def is for save data in file.
    def save(self):
        path_of_result = tat_datactrl.get_path("path_of_result")
        result_file_name = "{0}/limitation_magnitude_and_noise/delta_mag.fits".format(path_of_result)
        result = self.set_result()
        # Check whether the file exist or nat.
        try:
            pre_table = Table.read(result_file_name)
        # If not exist, create a new one.
        except:
            result_title = np.array(["delta_mag", "e_delta_mag", "object", "scope", "band_used", "date", "method", "band_of_ref", "eccentricity"])
            result_table = Table(rows = [result], names = result_title)
            result_table.write(result_file_name, overwrite = True)
        # If exist, append data.
        else:
            pre_table.add_row(result)
            pre_table.write(result_file_name, overwrite = True)
        return

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 1
    # measure times
    start_time = time.time()
    # get property form argument
    argument = argv_ctrl(argv)
    # Match between ref and local catalog
    execution = main_process(argument.fits_name(), argument.band(), argument.ecc())
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
