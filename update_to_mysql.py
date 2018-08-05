#!/usr/bin/python
'''
Program:
    This is a program for updating data into mysql database. 
Usage: 
    update_to_mysql.py [table list]
Editor:
    Jacob975
20180805
#################################
update log
20180805 version alpha 1
    1. The code works
'''
import numpy as np
import time
from sys import argv

# update table to mysql
def update_to_mysql(table):
    # bla bla bla
    return 0

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 2:
        print "Wrong number of arguments"
        print "Usage: update_to_mysql.py [table list]"
        exit(1)
    table_name_list_name = argv[1]
    #----------------------------------------
    # Load table and update to mysql
    table_name_list = np.loadtxt(table_name_list_name, dtype = str)
    for table_name in table_name_list:
        table = np.loadtxt(table_name, dtype = object)
        failure = update_to_mysql(table)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
