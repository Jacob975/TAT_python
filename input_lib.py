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
                '# name',
                '# The name of source or the name of files',
                '',
                '# Ingress timing in JD',
                '',
                '# Egress timing in JD',
                '']
        np.savetxt('option_plotLC.txt', s, fmt = '%s')
    def load(self, file_name):
        self.opts = np.loadtxt(file_name, dtype = str)
        self.opts = list(self.opts)
        return self.opts
