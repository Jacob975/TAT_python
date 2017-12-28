#!/usr/bin/python
'''
Program:
This is a program to do catalog every day 1:00. 
Before conduct this code, please choose a correct folder.

Usage:
1. catalog_daemon.py
editor Jacob975
20171229
#################################
update log
    20171229 version alpha 1
    1. concept is built, code is finished, haven't been test.
'''

from datetime import datetime
from threading import Timer
import time

def job():
    paras = ["catalog_daemon", "-u"]
    mailer = argv_controller(paras)
    stu = cursor(mailer)
    return

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 0
    # measure times
    start_time = time.time()
    # set the time period
    x=datetime.today()
    y=x.replace(day=x.day+1, hour=1, minute=0, second=0, microsecond=0)
    delta_t=y-x
    secs=delta_t.seconds+1
    wk = Timer(secs, job)
    wk.start()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
