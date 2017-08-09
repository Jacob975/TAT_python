#!/usr/bin/python
'''
Program:
This is a easier way to find needed flat.
method: 
1. Choose a folder you like 
2. $findflat.py
editor Jacob975
20170219 version alpha 1
#################################
update log
20170219 alpha 1
    It can run properly, but lot of error information come out when running.

20170310 alpha 2
    change the func. of find flat,
    Flats would been choose if there are 5 flat been taken on that day.

20170807 alpha 3
    fix a bug about finding the wrong flat.

20170808 version alpha 4 
    1.  Before we get path of calibrate by path of images.
        now we get path of calibrate from tat_config which is a setting file.
'''

import os
import fnmatch
import tat_datactrl

def readfile(filename):
    file = open(filename)
    answer_1 = file.read()
    answer=answer_1.split("\n")
    return answer

def match_date(date, date_list):
    # comfirm the type of date and datelist is int.
    if len(date_list) == 0:
        return -1
    date=int(date)
    new_date_list = []
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

def get_flat_to(telescope, filters, date, path_of_median_flat):
    # find out how many object in this folder
    temp_path=os.getcwd()
    obj_list=os.listdir(temp_path)
    # if it is a folder, get in and copy all flats in it to path of median flat.
    for name in obj_list:
        if os.path.isdir(name):
            temp_filters="flat_"+filters+"_*"
            if fnmatch.fnmatch(name, temp_filters):
                os.chdir(name)
                date=int(date)
                taken_date=date%1000000
                taken_date_next=taken_date+1
                taken_date=str(taken_date)
                taken_date_next=str(taken_date_next)
                # check if the number of avaliable flat is more than 5.
                temp="ls "+filters+"flat"+telescope+taken_date_next+"_*.fit "+filters+"flat"+telescope+taken_date+"_*.fit"+" > list"
                os.system(temp)
                fit_list=readfile("list")
                del fit_list[-1]
                if len(fit_list)<5:
                    print "Flat on "+str(date)+" is less than 5."
                    answer=len(os.listdir(path_of_median_flat))
                    print "now, the number of proper flat is: "+str(answer)
                    os.chdir("..")
                    return answer
                temp="cp -R "+filters+"flat"+telescope+taken_date+"_*.fit "+path_of_median_flat
                os.system(temp)
                temp="cp -R "+filters+"flat"+telescope+taken_date_next+"_*.fit "+path_of_median_flat
                os.system(temp)
                answer=len(os.listdir(path_of_median_flat))
                print "now, the number of proper flat is: "+str(answer)
                os.chdir('..')
                return answer
    answer=len(os.listdir(path_of_median_flat))
    return answer
    
def get_exptime(filters):
    exptime=""
    path=os.getcwd() 
    obj_list=os.listdir(".")
    for name in obj_list:
        if fnmatch.fnmatch(name, "flat_"+filters+"_*"):
            temp=name.split("_")
            exptime=temp[2]
    return exptime

def find_exptime(date, date_list, filters):
    exptime=""
    temp_date_list = date_list[:]
    result_date=match_date(date, date_list)
    if result_date == -1 :
        print "date list has been zero"
        return -1
    os.chdir(result_date[1])
    exptime=get_exptime(filters)
    os.chdir("..")
    if exptime=="":
        del temp_date_list[result_date[0]]
        exptime=find_exptime(date, temp_date_list, filters)
    return exptime

def sub_process(telescope, filters, result_date, path_of_median_flat, date, date_list):
    del date_list[result_date[0]]
    # find new match date
    result_date=match_date(date, date_list)
    if result_date == -1:
        print "date list has been zero"
        return -1
    os.chdir(result_date[1])
    # get more flat fit
    number=get_flat_to(telescope, filters, result_date[1], path_of_median_flat)
    os.chdir("..")
    # recursive condition
    if result_date == -1: 
        return -1
    if number<10:
        number=sub_process(telescope, filters, result_date, path_of_median_flat, date, date_list)
    return number

def main_process():
    # get original path as str and list
    path=os.getcwd()
    list_path=path.split("/")
    del list_path [0]
    # get info from path
    date=list_path[-3]
    telescope = list_path[-5]
    # get filters from path
    temp=list_path[-1]
    temp_list=temp.split("_") 
    filters=temp_list[0] 
    # go to the dir of calibrate
    path_of_source = tat_datactrl.get_path("path_of_source")
    path_of_calibrate="{0}/{1}/calibrate".format(path_of_source, telescope)
    os.chdir(path_of_calibrate)
    # get a list of all object in calibrate
    date_list=os.listdir(path_of_calibrate)
    # find the nearest date reference to original date.w
    result_date=match_date(date , date_list)
    if result_date == -1:
        print "date list has been zero, program ended"
        return -1
    # determind the exptime of flat
    exptime=find_exptime(date, date_list, filters)
    if exptime == -1 :
        print "date list has been zero"
        return -1
    # defind the dir of median flat, if it doesn't exist , create it.
    path_of_median_flat = path_of_source+"/"+telescope+"/calibrate/"+result_date[1]+"/median_flat_"+filters+"_"+exptime
    print "path of median flat is :"+path_of_median_flat
    if os.path.isdir(path_of_median_flat):
        temp="rm -r "+path_of_median_flat
        os.system(temp)
    temp="mkdir -p "+path_of_median_flat
    os.system(temp)
    # get flat
    os.chdir(result_date[1])
    print os.getcwd()
    number=get_flat_to(telescope, filters, result_date[1], path_of_median_flat)
    os.chdir("..") 
    if number<10:
        number=sub_process(telescope, filters, result_date, path_of_median_flat, date, date_list)
    if number<10:
        print "The number of flat is not enough, no median flat create."
        return 0
    os.chdir(path_of_median_flat)
    temp="finddark.py"
    os.system(temp)
    temp="rm Median_flat*"
    os.system(temp)
    temp="median_flat.py "+filters
    os.system(temp)
    temp='cp Median_flat*n.fits '+path
    os.system(temp)
    os.chdir(path)

main_process()
