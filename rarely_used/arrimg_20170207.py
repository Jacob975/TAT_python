#!/usr/bin/python
'''
Program:
This is a easier way to arrange images with different filters.
method: 
1. Choose a folder you like 
2. $arrimg.py
editor Jacob975
20170207 version alpha 5
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
'''
import os
import pyfits

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    while answer[-1] == "":
        del answer[-1]
    return answer

#create a list of images
os.system("ls *fit > list")
imagelist=readfile("list")

#create a list of object
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

sample_list=[IC5146, NGC1333, WD1253, SgrNova, HH32, KIC8462852, KELT_17,Groombridge1830, PN, Cygni61]

sample_count=[[[ 0 for z in range(2) ] for x in range(26)] for y in range(len(sample_list))]

# count filters and objects
for i in range(len(imagelist)):
    # get the RA and DEC of the fits
    darkh=pyfits.getheader(imagelist[i])
    fin_RA=darkh['RA'].split(':')
    fin_DEC=darkh['DEC'].split(':')
    # Dose the target in the list of sample?
    # If true, record the exptime, and how many fits of each sample.
    for j in range(len(sample_list)):
        ini_RA=sample_list[j]['RA'].split(':')
        ini_DEC=sample_list[j]['DEC'].split(':')
        if fin_RA[0] == ini_RA[0]:
            if fin_DEC[0] == ini_DEC[0]:
                templist=imagelist[i].split('Star')
                for k in range(26):
                    if chr(65+k)==templist[0]:
                        if sample_count[j][k][1]== 0 :
                            time=int(darkh['EXPTIME'])
                            sample_count[j][k][1]=str(time)
                        sample_count[j][k][0]=sample_count[j][k][0]+1
                        break
                break

#create folders

for i in range(len(sample_count)):
    for j in range(len(sample_count[i])):
        if sample_count[i][j][0] != 0:
            temp="mkdir -p "+sample_list[i]['name']+"/"+chr(65+j)+"_"+sample_count[i][j][1]+"s"
            os.system(temp)
k=0
# move fit to assigned folders with the RA ,DEC and exptime.
for name in imagelist:
    templist=name.split('Star')
    darkh=pyfits.getheader(name)
    fin_RA=darkh['RA'].split(':')
    fin_DEC=darkh['DEC'].split(':')
    for i in range(len(sample_list)):
        ini_RA=sample_list[i]['RA'].split(':')
        ini_DEC=sample_list[i]['DEC'].split(':')
        if fin_RA[0]==ini_RA[0]:
            if fin_DEC[0]==ini_DEC[0] : 
                for j in range(26-k): 
                    if templist[0]==chr(65+j+k):
                        temp="mv "+name+" "+sample_list[i]['name']+"/"+chr(65+j+k)+"_"+str(sample_count[i][j+k][1])+"s"
                        os.system(temp)
                        k=j
                        break
                break
