#!/usr/bin/python
'''
Program:
This is a easier way to test the completeness of CCDTEMP, EXPTIME, RA, and DEC.
It also check if CCDTEMP < -29.5 deg.
then arrange your images, 
find proper dark, 
do subdark, 

method:
0. You need alias /home/Jacob975/bin/python/arrimg.py
1. Choose a folder you like 
2. $chkarrimg.py
editor Jacob975
20170216
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

20170803 alpha 4
    1.  adjust the restriction about mean of data
        mean mention before is renamed as background (bkg).
        Now the program will not judge a image only with bkg value.
        The program will read bkg and noise of all images ,and kick out the exotic one.
    2.  The program will write down log now.

20170807 alpha 5
    1.  Change program path from 'python' to 'tat_python'.
'''
import os 
import pyfits
import numpy as np
import curvefit
import glob
# controll how many info will be print on screen.
# 0: no print
# 1: print result
# 2: print graph
# 3: print debug
VERBOSE = 1
# read a list of images
# also create array of bkg and noise.
image_list = glob.glob('*.fit')
bkg_array = np.array([ 0 for i in range(len(image_list)) ])
noise_array = np.array([ 0 for i in range(len(image_list)) ])
#create a list of parameters
paras=['CCDTEMP','EXPTIME','RA','DEC']
bad_img_count = 0
#check images by some phys property
for i in xrange(len(image_list)):
    darkh=pyfits.getheader(image_list[i])
    # If this fits lack one of header info in paras, abandom this fit.
    wrong = False
    for para in paras:
        try :
            temp_a=darkh[para]
        except KeyError:
            bad_img_count += 1
            temp = "mv {0} X_{0}_X".format(image_list[i])
            os.system(temp)
            wrong = True
            break
    if wrong:
        continue
    # If the ccd temperature is too high, abandom this fit.
    img_temp=darkh['CCDTEMP']
    if img_temp >= -29.5:
        bad_img_count += 1
        temp = "mv {0} X_{0}_X".format(image_list[i])
        os.system(temp)
        continue
    # save the bkg and stdev of each img.
    data = pyfits.getdata(image_list[i])
    params, cov = curvefit.hist_gaussian_fitting("default", data, shift = -7)
    data_mean = params[0]
    data_std = params[1]
    if VERBOSE>1:print "mean = {0}, stdev = {1}".format(data_mean, data_std)
    bkg_array[i] = data_mean
    noise_array[i] = data_std
    if VERBOSE>0:print image_list[i], ",checked"

# check whether the image over exposure or not.
mean_bkg = np.mean(bkg_array[np.nonzero(bkg_array)])
std_bkg = np.std(bkg_array[np.nonzero(bkg_array)])
temp_bkg_array = np.subtract(bkg_array, mean_bkg)
abs_bkg_array = np.absolute(temp_bkg_array)

mean_noise = np.mean(noise_array[np.nonzero(noise_array)])
std_noise = np.std(noise_array[np.nonzero(noise_array)])
temp_noise_array = np.subtract(noise_array, mean_noise)
abs_noise_array = np.absolute(temp_noise_array)

for i in xrange(len(image_list)):
    if abs_bkg_array[i] >= 3 * std_bkg:
        bad_img_count += 1
        temp = "mv {0} X_{0}_X".format(image_list[i])
        os.system(temp)
        continue
    elif abs_noise_array[i] >= 3 * std_noise:
        bad_img_count += 1
        temp = "mv {0} X_{0}_X".format(image_list[i])
        os.system(temp)
        continue
# print and write down the log
if VERBOSE>0:
    print "Number of total image: {0}".format(len(image_list))
    print "Number of success: {0}".format(len(image_list) - bad_img_count)
    print "Number of fail: {0}".format(bad_img_count)
    print "check end\n##################################"

log_file = open("log", "a")
log_file.write("log from: /home/Jacob975/bin/tat_python/chkarrimg.py")
log_file.write("# Number of total image: {0}\n".format(len(image_list)))
log_file.write("# Number of success: {0}\n".format(len(image_list) - bad_img_count))
log_file.write("# Number of fail: {0}\n".format(bad_img_count))
log_file.close()
# arrange images
os.system("arrimg.py")

# create subdark_fits for all kinds of filters and objects.
obj_list=os.listdir(".")
for name_obj in obj_list:
    if os.path.isdir(name_obj):
        os.chdir(name_obj)
        filter_list=os.listdir(".")
        for name_filter in filter_list:
            if os.path.isdir(name_filter):
                os.chdir(name_filter)
                temp="finddark.py"
                os.system(temp)
                temp="findflat.py"
                os.system(temp)
                temp="sub_div_r.py"
                os.system(temp)
                os.chdir("..")
        os.chdir("..")   
