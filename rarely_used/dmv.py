#!/usr/bin/python
'''
Program:
This is a easier way to move all done images in folder to /home/Jacob975/[telescope]/done_fits/[some folder].
method: 
1. Choose a folder you like 
2. $dmv.py
editor Jacob975
20170218 version alpha 3
#################################
update log

20170214 alpha 1
    It can move properly, but create extra folders.

20170215 alpha 2
    extra folders will be delete.

20170218 alpha 3
    add a def of rmove folder, now it will do rmove empty folder by itself.

20170304 alpha 4
    improve the effecience, change directions to /home/james/TAT_done/[TBA]
'''
import os 
import fnmatch

def rm_ept_dir():
    path=os.getcwd()
    obj_list=os.listdir(path)
    if obj_list==[]:
        temp="rm -R "+path
        os.system(temp)
        return 0
    for name in obj_list:
        if os.path.isdir(name):
            os.chdir(name)
            rm_ept_dir()
            os.chdir("..")
    return 0

def move_what_I_want():
    present_dir=os.getcwd()
    temp_dir=present_dir.split("/")
    del temp_dir [0]
    new_dir=""
    if len(temp_dir)==7:
        temp_list=temp_dir[-1].split("_")
        filters=temp_list[0]
        exptime=temp_list[1]
        new_dir="/brick/TAT_done/"+temp_dir[-2]+"/"+temp_dir[3]+"/"+filters+"/"+exptime+"/"+temp_dir[-3]
        if os.path.isdir(new_dir)!=True:
            temp="mkdir -p "+new_dir+" -m 774"
            os.system(temp)
    imagelist=os.listdir(present_dir)
    for name in imagelist:
        if os.path.isfile(name):
            if fnmatch.fnmatch(name, '*_m.fits'):
                temp="cp -R "+name+" "+new_dir
                print temp
                os.system(temp)
                continue
        elif os.path.isdir(name):
            os.chdir(name)
            move_what_I_want()
            os.chdir("..") 

move_what_I_want()

#remove empty folder
for i in range(3):
    rm_ept_dir()
