#!/usr/bin/python
'''
Program:
This is a program to test the. 
Usage:
1. table_example.py 
editor Jacob975
20170817
#################################
update log

20170817
'''
import numpy as np
import time
from astropy.table import Table

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # get property from argv 
    #--------------------------------------------
    # first example
    # setup a basic table
    print "--- first ---"
    a = [1, 4, 5]
    b = [2.0, 5.0, 8.2]
    c = ['x', 'y', 'z']
    t = Table([a, b, c], names=('a', 'b', 'c'), meta={'name': 'first table'})
    
    if VERBOSE>0:print t

    #--------------------------------------------
    # second example
    # setup a basic table in another way
    # unit controlling test.
    print "--- second ---"
    data_rows = [(1, 2.0, 'x'), 
                (4, 5.0, 'y'),
                (5, 8.2, 'z')]
    t = Table(rows=data_rows, names=('a', 'b', 'c'), meta={'name': 'first table'}, dtype=('i4', 'f8', 'S1'))
    t['b'].unit = 's'
    if VERBOSE>0:
        print t
        print t.info
        print t['b'].quantity
        print t['b'].to('min')
    # show_in_notebook do no reaction, I don't know why.
    t.show_in_notebook()
    #---------------------------------------------
    # third example
    # type of saved file
    # currently, the most suitable one is .fits
    t.write('table.fits')
    u = Table.read('table.fits')
    print u.info
    #---------------------------------------------
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
