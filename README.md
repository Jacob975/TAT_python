Warning: I rarely update this file because I have no time and also the code update pretty freqently, make any intro on any version is not smart way currently.

so please do not take this file as reference.

# tat_python
Program for sorting and processing images of TAT telescope

# Preparation

1. Install python or python2 in your computer, recommand python-2.7.13

2. install extra python module below

	numpy
	photutils
	scikit-image
	PyAstronomy
	astropy
	scipy
3. Install packages
	
	python-devel for CentOS

	python-dev for Ubuntu

You can install these module by this command: $python -m pip install modulename

If you want only install locally, please use this command: $ python -m pip install --user modulename

3. install ds9 package

You can access ds9 by yum(for rat-hat), or apt-get(for ubuntu), or homebrew(for mac)

4. install x11 (for remote user)

If you use tat code in remote server, you should install x11 or some program using $display cannot execute.

# Setup
1. $vim TAT_env.py 

	set path of tat code, source(your raw data), python, and result in tat_config

2. $tat_setup.py

	This code will set up all folder you need, set the python path in each tat program.

# Standard Steps of processing TAT Data.

1. data_reduction.py

    TBA
