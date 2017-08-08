#!/usr/bin/python
'''
Program:
This is a easier way to download lots of result of coordinates from nova.astrometry.net and correspond to original images.
method: 
1. $wgetastro.py [job numbers][original list]
    job numbers:        THe list of images which is created by nova.astrometry.net, you can easily see them on corresponding result pages.
    original list:	The list of imgaes you upload to nova.astrometry.net. 

2. $wgetastro.py [job number][original]
    job number: literally, the job number of file on astrometry.
    original :  The name of dropped file

editor Jacob975 
20170118
##############################
update log

alpha 1:    20170117:
    the program can run properly, but I haven't put it in alias.

alpha 2:    20170118:
    the program con run, include alias and explaination.
    But the program can not detect Is the input type is correct or not, 
    as well as preventing itself from type error.

alpha 3:    20170706:
    add a new func such that we can do a fits straightly, it is much more efficient.

alpha 4:    20170720:
    It will also save data in /home/Jacob975/demo/TAT_done/

20170808 version alpha 5:
    1.  use tat_config to control path of result data instead of fix the path in the code.
'''   

import os
from sys import argv, exit
import tat_datactrl

jobnumberlistname = argv[1]
originallistname = argv[2]

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while (answer[-1] == "") :
        del answer[-1]
    return answer

def readfileplus(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("subDARK.fits\n")
    while (answer[-1] == "") :
        del answer[-1]
    return answer

def printlist(array):
    for i in range(len(array)):
        print array[i]

# If only one jobnumber, this code will do 
try :
    jobnumberlistname = int(jobnumberlistname)
except:
    originallist = readfileplus(originallistname)
    jobnumberlist = readfile(jobnumberlistname)
else:
    command = "wget 'http://nova.astrometry.net/new_fits_file/{0}' -O {1}".format(jobnumberlistname, originallistname)
    os.system(command)
    path_of_result = tat_datactrl.get_path("result")
    command = "cp {0} {1}/TAT_done/{0}".format(originallistname, path_of_result)
    os.system(command)
    exit(0)

file = open('download','w')
for i in range(len(originallist)-1) :
    temp="wget 'http://nova.astrometry.net/new_fits_file/" + jobnumberlist[i] + "' -O " + originallist[i] + "subDARK_r_3s_w.fits\n"
    print temp
    file.write(temp)
file.close()


