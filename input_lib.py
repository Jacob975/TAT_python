#!/usr/bin/python
'''
Abstract:
    This is a program for reading and loading input files. 
Usage:
    input_lib.py
Editor:
    Jacob975

20181204
####################################
update log
20181204 version alpha 1
    1. The code works.
'''
import numpy as np
import time

class option_plotLC():
    def __init__(self):
        self.opts = None
    def create(self):
        s = [   '# Where to get data',
                '# 1: from given filename, and the name become the filename.',
                '# 2: from database, and the name become the target name',
                '2',
                '# Catalog name',
                '# The name of source or the name of files',
                '',
                '# Common name',
                '# The common name of the source',
                '',
                '# Ingress timing in JD',
                '# "skip" means it would not print the ingress timing on plots.',
                'skip',
                '# Egress timing in JD',
                '# "skip" means it would not print the ingress timing on plots.',
                'skip',
                '# Start date in YYYYMMDD',
                '# The first date of the plot showing. Input image folder date minus one.',
                '# "skip" will make the program shows all light curves.',
                'skip',
                '# End date in YYYYMMDD',
                '# The last date of the plot showing.',
                '# "skip" will make the program shows all light curves.',
                'skip',
                '# Band',
                '# Available options: N, C, A, V, B, R',
                'V',
                '# Exptime',
                '# The exposure time of selected images',
                '150',
                '# Path of photometry option file',
                '# e.g. /home2/TAT/programs/TTV/photometry/',
                '',
                '# Name of photometry option file',
                'option_phot_'
                ]
        np.savetxt('option_plotLC.txt', s, fmt = '%s')
    def load(self, file_name):
        self.opts = np.loadtxt(file_name, dtype = str)
        self.opts = list(self.opts)
        return self.opts

class option_plot_auxLC():
    def __init__(self):
        self.opts = None
    def create(self):
        s = [   '# Where to get data',
                '# 1: from given filename, and the name become the filename.',
                '# 2: from database, and the name become the target name',
                '2',
                '# name',
                '# The name of auxiliary star or the name of files',
                '',
                '# Start date in YYYYMMDD',
                '# The first date of the plot showing.',
                '# "skip" will make the program shows all light curves. Input image folder date-1.',
                'skip',
                '# End date in YYYYMMDD',
                '# The last date of the plot showing.',
                '# "skip" will make the program shows all light curves.',
                'skip',
                '# Band',
                '# Available options: N, C, A, V, B, R',
                'V',
                '# Exptime',
                '# The exposure time of selected images',
                '150'
                ]
        np.savetxt('option_plot_auxLC.txt', s, fmt = '%s')
    def load(self, file_name):
        self.opts = np.loadtxt(file_name, dtype = str)
        self.opts = list(self.opts)
        return self.opts

class option_photometry():
    def __init__(self):
        self.opts = None
    def create(self):
        s = [   '# What kinds of photometry calibration you want',
                '# Available options: EP, CATA.',
                '#  EP: Ensemble Photometry',
                '#  CATA: Calibrate the magnitude with I/329 catalog',
                'EP',
                '# The date of starting observation',
                '# example: 20181208',
                '',
                '# The date of end observation',
                '# Input image folder date minus one.'
                '# example: 20181209',
                '',
                '# RA centroid (deg)',
                '# What is the right ascention of the center of FOV.',
                '# example: 239.00',
                '',
                '# DEC centroid (deg)',
                '# What is the declination of the center of FOV.',
                '# example: 15.00',
                '',
                '# Band',
                '# Available options: N, C, A, V, B, R',
                '# You could type "skip" to ignore this selection.',
                'V',
                '# Exptime',
                '# The exposure time of selected images',
                '# You could type "skip" to ignore this selection.',
                '150',
                '# ID of beginning auxiliary star',
                '# From which auxiliary star you want to start with while doing photometry.',
                '# example: 10',
                '',
                '# Number of auxiliary stars',
                '# How many stars do you want to use for photometry.',
                '# example: 20',
                '20',
                '# The target name of variables',
                '# The program will ignore these stars since their luminosity might changed.',
                '# example: target_322.3157_50.8781',
                '# You could type "skip" to ignore this selection',
                'skip'
                ]

        np.savetxt('option_phot.txt', s, fmt = '%s')
    def load(self, file_name):
        self.opts = np.loadtxt(file_name, dtype = str)
        self.opts = list(self.opts)
        return self.opts
