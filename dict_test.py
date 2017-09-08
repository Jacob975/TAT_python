#!/usr/bin/python
'''
Program:
This is a program to test the property of dict
Usage:
1. dict_test.py
editor Jacob975
20170908
#################################
update log

20170908 version alpha 1
'''
import time

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()

    keywords = {'date':'a', 'scope':'a', 'band':'a', 'method':'a', 'object':'a', 'exptime':600} 
    print len(keywords)
    print keywords
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
