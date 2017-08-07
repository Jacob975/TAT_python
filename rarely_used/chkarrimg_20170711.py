#!/usr/bin/python
'''
Program:
This is a easier way to test the completeness of CCDTEMP, EXPTIME, RA, and DEC.
It also check if CCDTEMP < -29.5 deg.
then arrange your images, 
find proper dark, 
do subdark, 
create a tar which is used to uploaded to Astrometry.net.

method:
0. You need alias /home/Jacob975/bin/python/arrimg.py
1. Choose a folder you like 
2. $chkarrimg.py
editor Jacob975
20170216 version alpha 2
#################################
update log

20170206 alpha 1 
    It can run properly.

20170216 alpha 2 
    Make code more efficient, add a link code to find darks and subdark.
    It out of work now, fixing...

20170711 alpha 3 
    add a new restriction on proper fit
    Now if the mean of data is more than 1550 count, this fit will be eliminate.
'''
import os 
import pyfits
import numpy as np
import curvefit

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
#create a list of parameters
paras=['CCDTEMP','EXPTIME','RA','DEC']
#check images by some phys property
for name in imagelist:
    darkh=pyfits.getheader(name)
    # If this fits lack one of header info in paras, abandom this fit.
    wrong = False
    for para in paras:
        try :
            temp_a=darkh[para]
        except KeyError:
            temp="mv "+name+" X_"+name+"_X"
            os.system(temp)
            wrong = True
            break
    if wrong:
        continue
    # If the ccd temperature is too high, abandom this fit.
    img_temp=darkh['CCDTEMP']
    if img_temp >= -29.5:
        temp="mv "+name+" X_"+name+"_X"
        os.system(temp)
        continue
    # If the backgrond is too high, abandom this fit.
    data = pyfits.getdata(name)
    data_mean, data_std = curvefit.get_mean_std(data)
    if data_mean > 1550:
        temp="mv "+name+" X_"+name+"_X"
        os.system(temp)
        continue
# arrange images
os.system("python /home/Jacob975/bin/python/arrimg.py")

# create subdark_fits for all kinds of filters and objects.
obj_list=os.listdir(".")
for name_obj in obj_list:
    if os.path.isdir(name_obj):
        os.chdir(name_obj)
        filter_list=os.listdir(".")
        for name_filter in filter_list:
            if os.path.isdir(name_filter):
                os.chdir(name_filter)
                temp="python /home/Jacob975/bin/python/finddark.py"
                os.system(temp)
                temp="python /home/Jacob975/bin/python/findflat.py"
                os.system(temp)
                temp="python /home/Jacob975/bin/python/sub_div_r.py"
                os.system(temp)
                os.chdir("..")
        os.chdir("..")   
