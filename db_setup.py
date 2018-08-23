#!/usr/bin/python
'''
Program:
    This is a program for setting up databases for TAT data.
Usage: 
    db_setup.py
Editor:
    Jacob975
20180822
#################################
update log
20180822 version alpha 1
    1. The code works
'''
import numpy as np
import time
from sys import argv
import mysqlio_lib

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    mysqlio_lib.create_TAT_tables()    
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
