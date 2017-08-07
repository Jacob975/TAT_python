#!/usr/bin/python
'''
Program:
This is a program, match images with _subDARK_r or _subDARK_divFLAT_r.
create _subDARK_r_m or _subDARK_divFLAT_r_m
you need setenv of /home/james/shift_compute/match_frames.
method: 
1. Choose a folder you like, which contain flat.fits 
2. $mtcimg.py [header]
editor Jacob975
20170302 version alpha 2
#################################
update log

20170301 alpha 1
    It can run properly

20170302 alpha 2
    add a new func to find reference and create new reference.

20170304 alpha 3
    fix a bug about choose reference image.
    add a little feedback text.

20170305 alpha 4
    now, the reference is the same for diff. filters.
'''
import os
import fnmatch
from sys import argv
from sys import exit

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

def find_reference(figure, local_figure, obj_name, img_list, ref_path, path):
    os.chdir(ref_path)
    ref_list=os.listdir(".")
    for name in ref_list :
        if fnmatch.fnmatch(name, figure):
            temp="cp "+figure+" "+path
            os.system(temp)
            os.chdir(path)
            temp="mv "+figure+" "+local_figure
            os.system(temp)
            return True
    if header!="N":
        return False
    os.chdir(path)
    print "New reference is "+img_list[0]
    temp="cp "+img_list[0]+" "+ref_path
    os.system(temp)
    os.chdir(ref_path)
    temp="mv "+img_list[0]+" "+figure
    print temp
    os.system(temp)
    temp="cp "+figure+" "+path
    os.system(temp)
    os.chdir(path)
    temp="mv "+figure+" "+local_figure
    os.system(temp)
    return True
    
def do_match(header, obj_name):
    temp="ls "+header+"*_r.fits > list_rotated"
    os.system(temp)
    list_name="list_rotated"
    # create a temp folder to process matching.
    temp_folder="temp_folder"
    img_list=readfile(list_name)
    del img_list[-1]
    if img_list[0]=="":
        return False
    temp="mkdir "+temp_folder
    os.system(temp)
    temp="mv "+header+"_"+obj_name+"_r.fits "+temp_folder
    os.system(temp)
    # do match once in 20 fits
    for i in range(len(img_list)):
        temp="mv "+img_list[i]+" "+temp_folder
        os.system(temp)
        if i%20==0 and i!=0:
            os.chdir(temp_folder)
            temp="match_frames "+header+"*_r"
            os.system(temp)
            temp="mv "+header+"Star* .."
            os.system(temp)
            temp="rm "+header+"_"+obj_name+"_r_m.fits"
            os.system(temp)
            os.chdir("..")
    os.chdir(temp_folder)
    temp="match_frames "+header+"*_r"
    os.system(temp)
    temp="mv "+header+"Star* .."
    os.system(temp)
    temp="rm "+header+"_"+obj_name+"_r_m.fits"
    os.system(temp)
    os.chdir("..")
    return True

def clear(): 
    temp="rm -r temp_folder"
    os.system(temp)
    temp="rm *.mask"
    os.system(temp)

header=str(argv[1])
# get path 
path=os.getcwd()
list_path=path.split("/")
del list_path[0]
# set direction of reference 
ref_path="/home/Jacob975/reference"
# get object name
obj_name=list_path[-2]
# determind the name of reference
figure=obj_name+"_r.fits"
local_figure=header+"_"+obj_name+"_r.fits"
# get list of divFLAT
temp="ls "+header+"*_divFLAT_r.fits > list_divFLAT"
os.system(temp)
divFLAT_list=readfile("list_divFLAT")
del divFLAT_list[-1]
# find reference
suit=find_reference(figure, local_figure, obj_name, divFLAT_list, ref_path, path)
if suit==False:
    exit("There is no proper reference, program stop")
# do match
situ=do_match(header, obj_name)
if situ:
    clear()
    exit("match succeed.")
else:
    clear()
    exit("match failed.")
