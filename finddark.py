#!/usr/bin/python
'''
Program:
This is a easier way to find needed dark.
method: 
1. Choose a folder you like 
2. $finddark.py
editor Jacob975
20170216 version alpha 3
#################################
update log
20170215 alpha 1
    It can run properly.

20170216 alpha 2
    fix a bug about copy darks.

20170219 alpha 3
    fix a bug about error exptime.

20170808 version alpha 4
    1.  Before we get path of calibrate from path of images
        Now we get path of calibrate from tat_config which is a setting file.

20171201 version alpha 5
    1.  using TAT_env as a new constant pool
    2.  the stack part is using code what is not writed by me, so I replace it with mine.
'''

import os
import glob
import pyfits
import numpy as np
import fnmatch
import TAT_env

def match_date(date, date_list):
    # comfirm the type of date and datelist is int.
    date=int(date)
    new_date_list=[]
    for d in date_list:
        try : 
            int(d)
        except ValueError:
            continue
        else:
            new_date_list.append(int(d))
    date_list = new_date_list
    # get all delta between two dates.
    delta_list=[]
    for name in date_list:
        delta_list.append(abs(name-date))
    # find minimum and index of minimum.
    min_value=min(delta_list)
    min_index=delta_list.index(min_value)
    min_value=str(date_list[min_index])
    answer=[min_index, min_value]
    return answer

def stack_mdn_method(fits_list):
    data_list = []
    for name in fits_list:
        data = pyfits.getdata(name)
        data_list.append(data)
    data_list = np.array(data_list)
    sum_fits = np.median(data_list, axis = 0)
    return sum_fits

def get_dark_to(telescope, exptime, date, path_of_median_dark):
    # find out how many object in this folder
    temp_path=os.getcwd()
    obj_list=os.listdir(temp_path)
    # if it is a folder, get in and copy all darks in it to path of median dark.
    for name in obj_list:
        if os.path.isdir(name):
            temp_exptime="*_"+exptime
            if fnmatch.fnmatch(name, temp_exptime):
                print "There is avaliable dark in: "+temp_path
                os.chdir(name)
                date=int(date)
                little_date=date%1000000
                little_date_next=little_date+1
                little_date=str(little_date)
                little_date_next=str(little_date_next)
                temp="cp -R dark"+telescope+little_date+"_*.fit "+path_of_median_dark+" 2>/dev/null"
                os.system(temp)
                temp="cp -R dark"+telescope+little_date_next+"_*.fit "+path_of_median_dark+" 2>/dev/null" 
                os.system(temp)
                answer=len(os.listdir(path_of_median_dark))
                print "number of found dark: "+str(answer)
                os.chdir('..')
                return answer
    answer=len(os.listdir(path_of_median_dark))
    return answer
    
def main_process():
    # get original path as str and list
    path=os.getcwd()
    list_path=path.split("/")
    del list_path [0]
    # get info from path
    path_of_source = TAT_env.path_of_source
    temp_path = path.split(path_of_source)
    temp_path_2 = temp_path[1].split("/")
    date=temp_path_2[3]
    telescope = temp_path_2[1]
    # get exptime from path
    temp=list_path[-1]
    temp_list=temp.split("_")
    exptime=temp_list[-1]
    # go to the dir of calibrate 
    path_of_calibrate = path_of_source+"/"+telescope+"/calibrate"
    os.chdir(path_of_calibrate)
    # get a list of all object in calibrate
    obj_list=os.listdir(path_of_calibrate)
    # find the nearest date reference to original date.
    result_date=match_date(date , obj_list)
    # defind the dir of median dark, if it doesn't exist , create it
    path_of_median_dark = path_of_source +"/"+ telescope + "/calibrate/"+result_date[1]+"/dark_"+exptime
    print "path of median dark is :"+path_of_median_dark
    if os.path.isdir(path_of_median_dark)==False:
        temp="mkdir -p "+path_of_median_dark
        os.system(temp)
    # get dark
    os.chdir(result_date[1])
    number=get_dark_to(telescope, exptime, result_date[1], path_of_median_dark)
    os.chdir("..")
    # check whether the number of dark is enough, if no, find other darks.
    if number<10:
        del obj_list[result_date[0]]
        sub_process(path, telescope, obj_list, date, path_of_median_dark, exptime)
    else:
        os.chdir(path_of_median_dark)
        dark_list = glob.glob('dark*.fit')
        m_dark = stack_mdn_method(dark_list)
        Median_dark_name="Median_dark_"+date+"_"+exptime+".fits"
        print "The dark name is :"+Median_dark_name
        pyfits.writeto(Median_dark_name, m_dark, clobber= True)
        temp="cp -R "+Median_dark_name+" "+path
        os.system(temp)
    return

def sub_process(path, telescope, obj_list, date, path_of_median_dark, exptime):
    # find another proper date to find dark.
    result_date=match_date(date, obj_list)
    os.chdir(result_date[1])
    # get dark 
    number=get_dark_to(telescope, exptime, result_date[1], path_of_median_dark)
    os.chdir("..")
    # check if the number of dark is enough, if no, find other darks.
    if number<10 and len(obj_list)>1:
        del obj_list[result_date[0]]
        sub_process(path, telescope, obj_list, date, path_of_median_dark, exptime)
    else:
        os.chdir(path_of_median_dark)
        dark_list = glob.glob('dark*.fit')
        m_dark = stack_mdn_method(dark_list)
        Median_dark_name = "Median_dark_"+date+"_"+exptime+".fits"
        print "The dark name is :"+Median_dark_name
        pyfits.writeto(Median_dark_name, m_dark, clobber= True)
        temp="cp -R "+Median_dark_name+" "+path
        os.system(temp)
    return

main_process()
