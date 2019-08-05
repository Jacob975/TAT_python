#!/usr/bin/python
'''
Program:
    This is a script to convert the unit from h:m:s/d:m:s to degree/degree  
Usage: 
    hms2deg.py
Output:
    1. The number in degree.
Editor:
    Jacob975
20190805
#################################
update log
20190805 version alpha 1:
    1. The code works.
'''
from sys import argv
import numpy as np
import time
from astropy import units as u
from astropy.coordinates import SkyCoord
#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments
    if len(argv) != 3:
        print "The number of arguments is wrong."
        print "Usage: hms2deg.py [h:m:s] [d:m:s]"
    ra_hms = argv[1]
    dec_dms = argv[2]
    #----------------------------------------
    # Convert
    c = SkyCoord(   ra_hms, dec_dms, 
                    unit=(u.hourangle, u.deg), 
                    frame='icrs')
    ra_deg = c.ra.degree
    dec_deg = c.dec.degree
    print ra_deg, dec_deg
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
