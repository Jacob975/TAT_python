#!/usr/bin/python
'''
Program:
This is a program to return std dev, mean of a fits data. 
method:
1. get_stdev_mean.py [list name]
editor Jacob975
20170318 version alpha 1
#################################
update log
'''
from sys import argv
from statistics import mean
from math import pow
import threading
import Queue
import numpy as np
import pyfits
import time

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):  
        process_data(self.name, self.q)

def stdev(data_list,mean):
    summ=0
    for i in data_list:
        sub = i-mean
        summ += pow(sub, 2)
    summ /= 1048576
    stddev=pow(summ, 0.5)
    return stddev


def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            name = q.get()
            queueLock.release()
            imA = pyfits.getdata(name)
            imB = imA.flatten()
            fits_mean = mean(imB)
            fits_stdev = stdev(imB, fits_mean)
            temp = name+"\tstdev: "+str(fits_stdev)+"\tmean: "+str(fits_mean)+" "+threadName
            print temp 
        else:
            queueLock.release()
        time.sleep(1)

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer
# measure times
start_time = time.time()
# setup exit condition
exitFlag=0
# get all names of fits
list_name=argv[-1]
fits_list=readfile(list_name)
del fits_list[-1]
# create some variables for multi threading
queueLock=threading.Lock()
thread_list=[]
for i in range(20):
    thread_list.append("Thread-"+str(i))
workQueue=Queue.Queue(len(fits_list))
threads=[]
threadID=1
# fill the queue
queueLock.acquire()
for name in fits_list:
    workQueue.put(name)
queueLock.release()
# create new threads
for tname in thread_list:
    thread=myThread(threadID, tname, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1
# waiting for queue to empty
while not workQueue.empty():
    pass
# Notify threads it's time to exit
exitFlag = 1
# Wait for all threads to complete
for t in threads:
    t.join()
# measuring time
elapsed_time = time.time() - start_time
print "Exiting Main Thread, spending ", elapsed_time, "seconds."
