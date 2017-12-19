#!/usr/bin/python
'''
Program:
This is a program to build a catalog of tat images. 
and some following features
1. Input the ccs, output the plot of nearest object.
Usage:
1. tat_catalog.py
editor Jacob975
20171217
#################################
update log
    20171217 version alpha 1
    1.  
'''
from sys import argv
import numpy as np
import pyfits
import time
import TAT_env
import glob
import datetime
import tat_phot
import os
from tat_datactrl import readfile
from astropy.table import Table, Column, Row

# This class is used to arragne argument.
class argv_controller:
    # the data of this class is saved here
    # opt_list means all possible option you can use
    # -t means the program will resolve all image to construct the catalog
    # -u means the program will only resolve new image reference to the logger file to update the existed catalog.
    opt_list = ['-t', '-u']
    # opt means the option you choose
    # default by '-u'
    opt = '-u'
    # the name of the code
    code_name = None
    # the starting time
    START_TIME = None
    # the name of log
    # all thing the code do will be save in log file
    LOG_NAME = None
    # how load the code be
    VERBOSE = 2
    # ---------------------------------------------
    # initialized the class
    def __init__(self, argu_list, VERBOSE = 2):
        # set the VERBOSE
        self.VERBOSE = VERBOSE
        # arrange argument
        for argu in argu_list:
            # skip the first argu, which is usually the name of the code.
            if argu_list.index(argu) == 0:
                self.code_name = argu
                continue
            # the the option
            for opt in self.opt_list:
                if opt == argu:
                    self.opt = argu
        # set the initial time 
        self.START_TIME = time.time()
        # set the log name
        self.LOG_NAME = "{0}_tat_catalog.log".format(self.START_TIME)
        if VERBOSE>1: print "the log will be saved here: {0}".format(self.LOG_NAME)
        # write log 
        self.savelog()
        return
    def savelog(self):
        log_file = open(self.LOG_NAME, "a+")
        log_file.write("the option: {0}\n".format(self.opt))
        log_file.close()
        return
# This class is used to move from one image to another.
class cursor:
    # the data of this class is saved here
    # where were you execute the code
    path_of_execute = None
    # opt_list means all possible option you can use
    # -t means the program will resolve all image to construct the catalog
    # -u means the program will only resolve new image reference to the logger file to update the existed catalog.
    opt_list = ['-t', '-u']
    opt = '-u'
    # the name of code you conduct
    code_name = None
    # the timestamp of the starting time
    START_TIME = None
    # where are we save the log.
    LOG_NAME = None
    # how load the code be
    VERBOSE = 2
    # the list of processed data
    PROCESSED_FITS_LIST_NAME = "processed_list"
    processed_fits_list = None
    # the list of all image in this folder
    fits_name_list = None
    # the list of unprocessed data
    unprocessed_fits_list = None
    def __init__(self, arg_ctrl, VERBOSE = 2):
        # pass constants
        self.path_of_execute = os.getcwd()
        self.opt = arg_ctrl.opt
        self.code_name = arg_ctrl.code_name
        self.START_TIME = arg_ctrl.START_TIME
        self.LOG_NAME = arg_ctrl.LOG_NAME
        self.VERBOSE = VERBOSE
        # read log
        if self.opt == '-t':
            self.process_fits_list = []
        elif self.opt == '-u':
            self.processed_fits_list = readfile(self.PROCESSED_FITS_LIST_NAME)
        # determine which image will be process
        self.fits_name_list = glob.glob("*.fits")
        self.unprocessed_fits_list = list(set(self.fits_name_list) - set(self.processed_fits_list))
        # process
        worker = distributor(self.unprocessed_fits_list)
        # update the list of processed image
        self.writefile(self.unprocessed_fits_list)
        # write down log
        self.savelog()
        return
    # this class is used to update the list of processed image.
    def writefile(self):
        log_file = open(self.PROCESSED_FITS_LIST_NAME, "a+")
        time_stamp = datetime.datetime.fromtimestamp(self.START_TIME).strftime('%Y-%m-%d %H:%M:%S')
        log_file.write("# date: {0}\n".format(time_stamp))
        log_file.write("# Processed files:\n")
        if len(self.unprocessed_fits_list) == 0:
            log_file.write("#\tNo file in this process\n")
            log_file.write("# the end of this process.")
            log_file.close()
            return
        for name in self.unprocessed_fits_list:
            log_file.write("{0}\n".format(name))
        log_file.write("# the end of this process.")
        log_file.close()
        return
    def savelog(self):
        log_file = open(self.LOG_NAME, "a+")
        time_stamp = datetime.datetime.fromtimestamp(self.START_TIME).strftime('%Y-%m-%d %H:%M:%S')
        log_file.write("# date: {0}\n".format(time_stamp))
        log_file.write("# Processed files:\n")
        if len(self.unprocessed_fits_list) == 0:
            log_file.write("#\tNo file in this process\n")
            log_file.write("# the end of this process.")
            log_file.close()
            return
        for name in self.unprocessed_fits_list:
            log_file.write("{0}\n".format(name))
        log_file.write("# the end of this process.")
        log_file.close()
# This class is used to arrange raw star catalog to form a star catalog.
class distributor:
    # how load the code be
    VERBOSE = 2
    fits_list = None
    error = TAT_env.pix1/3600.0 * 6.0
    path_of_execute = os.getcwd()
    # where were you save this catalog
    path_of_catalog = "{0}/tat_test_catalog".format(TAT_env.path_of_result)
    def __init__(self, fits_list, VERBOSE = 2):
        # setting the constants
        self.VERBOSE = VERBOSE
        print "tolerate error: {0}".format(self.error)
        self.path_of_catalog = "{0}/tat_test_catalog".format(TAT_env.path_of_result)
        self.fits_list = fits_list
        for name in fits_list:
            # do tat phot
            worker = tat_phot.phot_control(name, "aperphot")
            # read table
            phot_table = worker.star_table
            paras = worker.paras
            # add image info parameters into table
            date = [paras.date for i in range(len(phot_table))]
            date_col = Column(name = "date", data = date)
            phot_table.add_column(date_col)
            phot_table["date"].unit = "yyyymmdd"
            band = [paras.band for i in range(len(phot_table))]
            band_col = Column(name = "band", data = band)
            phot_table.add_column(band_col)
            scope = [paras.scope for i in range(len(phot_table))]
            scope_col = Column(name = "scope", data = scope)
            phot_table.add_column(scope_col)
            method = [paras.method for i in range(len(phot_table))]
            method_col = Column(name = "method", data = method)
            phot_table.add_column(method_col)
            exptime = [paras.exptime for i in range(len(phot_table))]
            exptime_col = Column(name = "exptime", data = exptime)
            phot_table.add_column(exptime_col)
            phot_table["exptime"].unit = "sec"
            self.execute(phot_table, paras)
        return
    # this def is used to execute distributing
    def execute(self, star_table, paras):
        # switch to path of where are we save the catalog
        os.chdir(self.path_of_catalog)
        # distribute the table
        for i in xrange(len(star_table)):
            match_table_name = ""
            searching_list_length = 0
            RA = star_table[i]['RAJ2000']
            DEC = star_table[i]['DECJ2000']
            match_table_name, searching_list_length = self.finder(RA, DEC)
            if match_table_name == None:
                self.new_table(star_table[i], searching_list_length)
            else:
                self.append_table(star_table[i], match_table_name)
        os.chdir(self.path_of_execute)
        return
    # This code is used to find the match table of input RA and DEC.
    def finder(self, RA, DEC):
        # setting constants
        loc_RA = float(RA)
        loc_DEC = float(DEC)
        error = self.error
        # grab the list of possible match table 
        table_list = glob.glob("TAT{0}{1}_*.fits".format(int(RA), int(DEC)))
        if len(table_list) == 0:
            print "{0:.5f} {1:.5f} new".format(loc_RA, loc_DEC)
            return None, 0
        for table_name in table_list:
            # grab data from the selected table.
            table = Table.read(table_name)
            ref_RA = float(table[0]['RAJ2000'])
            ref_DEC = float(table[0]['DECJ2000'])
            # check they are match or not.
            RA_include = ref_RA - error < loc_RA and ref_RA + error > loc_RA
            DEC_include = ref_DEC - error < loc_DEC and ref_DEC + error > loc_DEC
            # if match, return existing table name.
            if RA_include and DEC_include:
                print "{0:.5f} {1:.5f} success".format(loc_RA, loc_DEC)
                return table_name, len(table_list)
        # if noting match, return None
        print "{0:.5f} {1:.5f} fail".format(loc_RA, loc_DEC)
        return None, len(table_list)
    # if the star is a new star, this def is used to setup a new table.
    def new_table(self, star_row, searching_list_length):
        # create a new table
        new_table = Table(star_row)
        path_of_table = "{0}/TAT{1}{2}_{3}.fits".format(self.path_of_catalog, int(star_row['RAJ2000']), int(star_row['DECJ2000']), searching_list_length)
        new_table.write(path_of_table, format = 'fits', overwrite = True)
        return
    # if the star is founded star, the def is used to append the row to a existed table.
    def append_table(self, star_row, match_table_name):
        path_of_table = "{0}/{1}".format(self.path_of_catalog, match_table_name)
        print path_of_table
        existing_table = Table.read(path_of_table)
        existing_table.add_row(star_row)
        existing_table.write(path_of_table, format = 'fits', overwrite = True)
        return
    # save log of this process.
    def savelog(self):
        return
# This class is used to check whether the star is stable or not
class analysis:
    def __init__(self):
        return

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    mailer = argv_controller(argv)
    stu = cursor(mailer)
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
