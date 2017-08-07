#!/usr/bin/python
'''
Program:
This is a easier way to arrange images with different filters.
method: 
1. Choose a folder you like 
2. $arrimg.py
editor Jacob975
20170207
#################################
update log

alpha 1:    20170121:
    it able to arrange images with the first alphabet.
    I am going to add a func , be able to arrange with the type of objects.

alpha 2:    20170124:
    Now it's able to arrange images with filters and objects!

alpha 3:    20170126:
    add new object, KET_17.

alpha 4:    20170206:
    cancel the limitation on minute in RA
    repair a bug such that create empty folder
alpha 5:    20170207:
    repair a bug of overlap exptime

20170803 version alpha 6:
    1.  improve the efficiency.
    2.  Rename variables to current version
    3.  The program will write down log now.
'''
import os
import pyfits
import glob

VERBOSE = 1
# read a list of images
image_list = glob.glob('*.fit')

# create a list of object
IC5146={'RA':'21:53:24','DEC':'47:16:00','name':'IC5146'}
NGC1333={'RA':'03:29:10','DEC':'31:21:57','name':'NGC1333A'}
WD1253={'RA':'12:55:38','DEC':'25:53:31','name':'WD1253+261'}
SgrNova={'RA':'18:36:57','DEC':'-28:55:42','name':'SgrNova'}
HH32={'RA':'19:20:30','DEC':'11:02:01','name':'HH32'}
KELT_17={'RA':'08:22:27','DEC':'13:44:07','name':'KELT-17'}
Groombridge1830={'RA':'11:52:58.8','DEC':'37:43:07.2','name':'Groombridge1830'}
KIC8462852={'RA':'20:06:15', 'DEC':'44:27:24', 'name': 'KIC8462852'}
PN={'RA':'21:29:58.42','DEC':'51:03:59.8','name':'PN'}
Cygni61={'RA':'21:06:53.9','DEC':'38:44:57.9','name':'61Cygni'}

object_list=[IC5146, NGC1333, WD1253, SgrNova, HH32, KIC8462852, KELT_17,Groombridge1830, PN, Cygni61]
band_list = ["A", "B", "C", "N", "R", "V" ]
object_count=[[[ 0 for z in range(2) ] for x in xrange(len(band_list))] for y in range(len(object_list))]

# count filters and objects
for i in range(len(image_list)):
    # get the RA and DEC of the fits
    darkh=pyfits.getheader(image_list[i])
    local_RA=darkh['RA'].split(':')
    local_DEC=darkh['DEC'].split(':')
    # Dose the target in the list of sample?
    # If true, record the exptime, and how many fits of each sample.
    for j in range(len(object_list)):
        ref_RA = object_list[j]['RA'].split(':')
        ref_DEC = object_list[j]['DEC'].split(':')
        if local_RA[0] == ref_RA[0]:
            if local_DEC[0] == ref_DEC[0]:
                templist=image_list[i].split('Star')
                for k in xrange(len(band_list)):
                    if band_list[k] == templist[0]:
                        if object_count[j][k][1]== 0 :
                            time = int(darkh['EXPTIME'])
                            object_count[j][k][1] = time
                        object_count[j][k][0] = object_count[j][k][0]+1
                        break
                break

#create folders
log_file = open("log", "a")
log_file.write("log from: /home/Jacob975/bin/python/arrimg.py")
for i in xrange(len(object_count)):
    for j in xrange(len(band_list)):
        if object_count[i][j][0] != 0:
            temp="mkdir -p {0}/{1}_{2}s".format(object_list[i]['name'], band_list[j], object_count[i][j][1])
            os.system(temp)
            log_sentence = "# Object : {0}, band: {1}, exptime: {2}, number: {3}".format(object_list[i]['name'], band_list[j], object_count[i][j][1], object_count[i][j][0])
            log_file.write(log_sentence+"\n")
            if VERBOSE>0:print log_sentence
log_file.close()

# move fit to assigned folders with the RA ,DEC and exptime.
for name in image_list:
    templist=name.split('Star')
    darkh=pyfits.getheader(name)
    local_RA=darkh['RA'].split(':')
    local_DEC=darkh['DEC'].split(':')
    for i in xrange(len(object_list)):
        ref_RA = object_list[i]['RA'].split(':')
        ref_DEC = object_list[i]['DEC'].split(':')
        if local_RA[0] == ref_RA[0]:
            if local_DEC[0] == ref_DEC[0] : 
                for j in xrange(len(band_list)): 
                    if templist[0] == band_list[j]:
                        temp="mv {0} {1}/{2}_{3}s".format(name, object_list[i]['name'], band_list[j], object_count[i][j][1])
                        os.system(temp)
                        break
                break
if VERBOSE>0:
    print "arrange end\n###########################"
