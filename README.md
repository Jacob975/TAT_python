# Installation guide for tat_image_calibration
Program for calibrating and reducting images of TAT telescope

# Preparation

1. Install python2 in your computer, recommand python-2.7.13

2. install extra python module below\
	numpy\
	photutils\
	scikit-image\
	astropy\
	scipy\

3. Install packages\
    You need python-devel for CentOS and python-dev for Ubuntu\
    You can install these module by this command for root user: $python -m pip install modulename\
    If you want only install locally, please use this command: $ python -m pip install --user modulename\

3. install ds9 package\
    You can access ds9 by yum(for rat-hat), or apt-get(for ubuntu), or homebrew(for mac)

4. install x11 (for remote user)\
    If you use tat code in remote server, you should install x11 or some program using $display cannot execute.

# Setup
1. $vim TAT_env.py\
	set path of code, image(your raw data), python, and catalog in TAT_env.py

2. $tat_setup.py\
	This code will set up all folder you need, set the python path in each tat program.

# Standard Steps of processing TAT Data.

1. Do_Data_Reduction.py\
    After sent this command, first, HQ checkes the log files to know which folders are unprocessed.\
    Check the headers and quality of darks and flats.\
    Check the headers and quality of images.\
    Arrange images into folders: /path_of_image/KU/image/date/target/band_exptime.\
    Find darks and flats for each catagory of images.\
    Do data reduction(subDARK, divFLAT, psf regist) on images in each catagory.\
    After reduction finished, HQ will save update the list of processed folders, and reply whose darks or flats is not found.\
