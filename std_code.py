#!/usr/bin/python
'''
Program:
    This is a standard code shows the style of my program.
Usage: 
    std_code.py
Editor:
    Jacob975
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
20180621 alaph 6
    1. rename the code
'''
import os 
from astropy.io import fits as pyfits
import numpy as np
from fit_lib import hist_gaussian_fitting
import glob
import time

# There are the parameters of header infos
PARAS=['CCDTEMP','EXPTIME','RA','DEC']

def check_header(name_image):
    darkh=pyfits.getheader(name_image)
    # If one of header info are lost, eliminate this image.
    for para in PARAS:
        try :
            temp_a=darkh[para]
        except KeyError:
            print "{0} in {1} is wrong.".format(para, name_image)
            return 1
    # If the ccd temperature is too high, abandom this fit.
    img_temp=darkh['CCDTEMP']
    if img_temp >= -29.5:
        print "Temperature is not allow\n{0} in {1}".format(img_temp, name_image)
        return 1
    return 0

# This func is used to get mean and std info of background.
def bkg_info(name_image):
    # save the bkg and stdev of each img.
    data = pyfits.getdata(name_image)
    params, cov = hist_gaussian_fitting("default", data, shift = -7)
    mean_bkg = params[0]
    std_bkg = params[1]
    return 0, mean_bkg, std_bkg

#--------------------------------------------
# Main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Completeness check
    # make a list with names of images in this directory
    image_list = glob.glob('*.fit')
    # check the valid of image_list
    if len(image_list) == 0:
        print "Error!\nNo image found"
        exit()
    #---------------------------------------
    # Initialize
    mean_bkgs = []
    std_bkgs = []
    #---------------------------------------
    # Header and check
    bad_img_count = 0
    # check headers of images, then load mean and std of background.
    for name_image in image_list:
        failure = check_header(name_image)
        if failure:
            bad_img_count += 1
            temp = "mv {0} X_{0}_X".format(name_image)
            os.system(temp)
            mean_bkgs.append(0)
            std_bkgs.append(0)
            continue
        failure, mean_bkg, std_bkg = bkg_info(name_image)
        mean_bkgs.append(mean_bkg)
        std_bkgs.append(std_bkg)
        print name_image, ",checked"
    #----------------------------------------
    # Image quality check
    # check whether the image over exposure or not.
    no_loss_in_mean_bkgs = np.where(mean_bkgs != 0)
    print "Number of total image: {0}".format(len(image_list))
    print "Number of success: {0}".format(len(image_list) - bad_img_count)
    print "Number of fail: {0}".format(bad_img_count)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
