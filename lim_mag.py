#!/usr/bin/python
'''
Program:
This is a program of generate the limitation magnitude from database.
Usage:
1. lim_mag.py [date] [scope] [band] [method] [exptime]

date:
    The date taking photos.
    It should be a 8-digits number.
    e.g. 20170724
    If you type in "a", you will get limitation magnitude on all date.

scope:
    The scope be used.
    It should be a "KU" or "TF".
    e.g. KU
    If you type in "a", you will get limitation magnitude on all scope.

band:
    The band we used.
    It should be a english letter.
    e.g. N
    If you type in "a", you will get all limitation magnitude on all band.

method:
    The method used to stack images.
    It should be "mdn" or "mean"
    e.g. mdn
    If you type in "a", you will get all limitation magnitude of all method.

obj:
    The main object in this image.
    It should be one of words in obj_list below.
    e.g. SgrNova
    If you type in "a", you will get all object.

exptime:
    The exptime of photo.
    It should be a number in sec.
    default : 600
    e.g. 600

Usage : 
    $lim_mag.py 600                             # exptime should be the lastest argument.
    $lim_mag.py 20170518 600                    # date will be set as 20170518.
    $lim_mag.py KU 600                          # scope will be set as KU.
    $lim_mag.py N 600                           # band will be set as N_40s.
    $lim_mag.py mdn 600                         # stack method will be set as mdn.
    $lim_mag.py 600                             # exptime will be set as 600s.
    $lim_mag.py SgrNova 600                     # object will be set as SgrNova.
    $lim_mag.py 20170518 KU 600                 # you can use two arguments. 
    $lim_mag.py KU 20170518 600                 # order of arguments is trivial.
    $lim_mag.py 20170518 TF N mdn 600           # you can use at most 5 arguments.

editor Jacob975
20170724
#################################
update log

20170724 version alpha 1
    It works properly.

20170801 version alpha 2
    1.  add new argument "object".
    2.  renew previous argument "band".
        details please read header file.

20170808 version alphca 3
    1.  use tat_config to control path of result data instead of fix the path in the code.

20170906 version alpha 4 
    1.  On classified, input and output remind the same.
    2.  Now the programm will save the result of your quest

20171109 version alpha 5
    1. Hotfix: a bug of wrong keywords, band and band_local
'''
from sys import argv
import numpy as np
import pyfits
import time
import TAT_env
import warnings
from astropy.table import Table

# This class is argv I/O
class argv_controller:
    keywords = {'date':'a', 'scope':'a', 'band':'a', 'method':'a', 'object':'a'}
    exptime = 600
    keywords_name_list = ["date", "scope", "band", "method", "object"]
    band_list = ["A", "B", "C", "V", "R", "N"]
    obj_list = ["NGC1333", "KELT-17", "Groombridge1830", "WD1253+261", "SgrNova", "HH32", "KIC8462852", "PN", "61Cygni", "IC5146"]
    def __init__(self, argument, VERBOSE=0):
        if len(argument) == 1:
            print "Usage: lim_mag.py [date] [scope] [band] [method] [object] [exptime]"
            return 
        elif len(argument) == 2:
            self.exptime = float(argument[-1])
            return 
        elif len(argument) > 2 or len(argument) < 8:
            for i in xrange(len(argument)):
                if i == len(argument) -1:
                    continue
                # Is it a date?
                try:
                    float(argument[i])
                except :
                    pass
                else:
                    self.keywords['date'] = argument[i]
                # Is it a scope?
                if argument[i] =="KU" or argument[i] == "TF":
                    self.keywords['scope'] = argument[i]
                # Is it a band?
                elif len(argument[i]) == 1:
                    for band in self.band_list:
                        if argument[i] == band:
                            self.keywords['band'] = band
                            continue
                # Is it a method?
                elif argument[i] == "mdn" or argument[i] == "mean":
                    self.keywords['method'] = argument[i]
                # Is it a object?
                else:
                    for obj in self.obj_list:
                        if obj == argument[i]:
                            self.keywords['object'] = obj
                            continue
            self.exptime = float(argument[-1])
            if VERBOSE>1: print self.keywords
            return 
        else:
            print "Usage: lim_mag.py [date] [scope] [band] [method] [object] [exptime]"
            return 

# This class is used to read fits table
# and then print or save the magnitude we search.
class fits_table_reader:
    del_mag_table = None
    inst_mag_table = None
    keywords_name_list = ["date", "scope", "band", "method", "object"]
    keywords = None
    exptime = 0
    def __init__(self, del_mag_table_name, inst_mag_table_name, VERBOSE = 0):
        self.del_mag_table = Table.read(del_mag_table_name)
        self.inst_mag_table = Table.read(inst_mag_table_name)
        if VERBOSE>1:
            print self.del_mag_table
            print self.inst_mag_table
        return
    # quest for match in keywords
    # keywords is a dict.
    def quest_interact(self, keywords, exptime):
        self.keywords = keywords
        self.exptime = exptime
        # wipeout the data having no business with keywords
        if VERBOSE>1: print "start clean del_mag_table"
        clean_del_mag_table = self.wipeout(self.del_mag_table)
        if VERBOSE>1: print "start clean inst_mag_table"
        clean_inst_mag_table = self.wipeout(self.inst_mag_table)
        # match data in two table
        if VERBOSE>0:
            print "\n   --- result of your quest ---\n"
        result_table = self.match(clean_del_mag_table, clean_inst_mag_table)
        # save the info you quest
        self.save(result_table)
        return
    # A auest for del_m for code
    def quest_del_mag(self, keywords, exptime, VERBOSE = 0):
        self.keywords = keywords
        self.exptime = exptime
        # wipeout the data having no business with keywords
        clean_del_mag_table = self.wipeout(self.del_mag_table, VERBOSE)
        return clean_del_mag_table['delta_mag'][0]
    # wipeout the data having no business with keywords
    def wipeout(self, table, VERBOSE = 0):
        # create a empty list with length of property list
        temp_table_list = [ None for i in range(len(self.keywords_name_list)) ]
        # append original list to back
        # It wiil seem as
        # temp_list = [   [], [], [], ... ,[tar_list]  ]
        temp_table_list.append(table)
        for i in xrange(len(self.keywords_name_list)):
            if VERBOSE>1:print "current property = {0}".format(self.keywords.keys()[i])
            # value a mean no limitation on this keywords.
            ref_table = temp_table_list[i-1]
            if self.keywords.values()[i] == "a":
                temp_table_list[i] = ref_table
            elif self.keywords.keys()[i] == "band":
                for row in ref_table:
                    if row[self.keywords.keys()[i]][0] == self.keywords.values()[i]:
                        try:
                            temp_table_list[i].add_row(row)
                        except:
                            temp_table = ref_table.info(out = None)
                            #if VERBOSE>1:print temp_table['name']
                            temp_table_list[i] = Table(rows = row, names = np.array(temp_table['name']))
            else:
                for row in ref_table:
                    if row[self.keywords.keys()[i]] == self.keywords.values()[i]:
                        # append to exist table.
                        try:
                            temp_table_list[i].add_row(row)
                        # if no exist, create a new one.
                        except:
                            temp_table = ref_table.info(out = None)
                            #if VERBOSE>1:print temp_table['name']
                            temp_table_list[i] = Table(rows = row, names = np.array(temp_table['name']))
            if VERBOSE>2:print temp_table_list[i]
        return temp_table_list[len(self.keywords_name_list)-1]
    # Determine this two data are the same at these orders.
    def match_data(self, inst_row, del_row):
        for name in self.keywords_name_list:
            if name == "band":
                if inst_row[name] == del_row["band_local"]:
                    continue
                else:
                    return False
            if inst_row[name] != del_row[name]:
                return False
        return True
    # match data in two table
    def match(self, clean_del_mag_table, clean_inst_mag_table):
        if VERBOSE>2:
            print clean_del_mag_table 
            print clean_inst_mag_table
        table_title = np.array(['amp', 'e_amp', 'const', 'e_const', 'delta_mag', 'e_delta_mag', 'date', 'scope', 'band', 'method', 'object', 'exptime'])
        # calculate limitation of magnitude
        result_table = None
        for inst_row in clean_inst_mag_table:
            for del_row in clean_del_mag_table:
                if self.match_data(inst_row, del_row):
                    sent = "" 
                    for key in self.keywords_name_list:
                        sent = "{0}{1}: {2}, ".format(sent, key, inst_row[key])
                    if VERBOSE>0: print sent
                    amp = float(inst_row['amp'])
                    e_amp = float(inst_row['e_amp'])
                    const = float(inst_row['const'])
                    e_const = float(inst_row['e_const'])
                    delta_m = float(del_row['delta_mag'])
                    e_delta_m = float(del_row['e_delta_mag'])
                    answer = amp*np.log10(self.exptime) + const + delta_m
                    if VERBOSE>0: print "for exptime = {0}, limitation magnitude = {1:.2f}".format(self.exptime, answer)
                    data = np.array([amp, e_amp, const, e_const, delta_m, e_delta_m, inst_row['date'], inst_row['scope'], inst_row['band'], inst_row['method'], inst_row['object'], self.exptime])
                    try:
                        result_table.add_row(data)
                    except:
                        result_table = Table(rows = [data], names = table_title)

        return result_table
    # save the info you quest
    def save(self, result_table):
        if result_table == None:
            print "No result"
            return
        result_table.write("mag_quest.fits", overwrite = True)
        print "your result is in mag_quest.fits"
        return

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 3
    # measure times
    start_time = time.time()
    warnings.filterwarnings("ignore")
    # get property from argv
    properties = argv_controller(argv, VERBOSE)
    # read delta_mag.fits and noise_in_mag.fits
    path_of_result = TAT_env.path_of_result
    path_of_del_m = path_of_result + "/limitation_magnitude_and_noise/delta_mag.fits"
    path_of_inst_m = path_of_result + "/limitation_magnitude_and_noise/noise_in_mag.fits"
    if VERBOSE>1:
        print path_of_inst_m
        print path_of_del_m
    magnitude = fits_table_reader(path_of_del_m, path_of_inst_m, VERBOSE)
    magnitude.quest_interact(properties.keywords, properties.exptime, VERBOSE)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
