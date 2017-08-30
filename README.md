# tat_python
Program for sorting and processing images of TAT telescope

# Preparation

1. Install python or python2 in your computer, recommand python-2.7.13

2. install extra python module below

	numpy
	pyfits
	tabulate
	photutils
	scikit-image

You can install these module by this command: $python -m pip install modulename

If you want only install locally, please use this command: $ python -m pip --user install modulename

3. install ds9 package

You can access ds9 by yum(for rat-hat), or apt-get(for ubuntu), or homebrew(for mac)

4. install x11 (for remote user)

If you use tat code in remote server, you should install x11 or some program using $display cannot execute.

# Setup
1. $vim tat_config

	set path of tat code, source(your raw data), python, and result in tat_config

2. $vim tat_datactrl.py

	set path of tat_config in tat_datactrl.get_path

3. $tat_setup.py

	This code will set up all folder you need, set the python path in each tat program.

# Standard Steps of processing TAT Data.

following will demo the common way to process TAT data.
I will not explain all details of code here.
Details remain in the header of each programs' source code.

0. $chkarrcal.py

	This code will first mark bad calibrate with X_*_X,
	and then arrange your calibrate in current folder.
	$mv them into different folder by band, and exptime.
	
	you should check all calibrate you have in [source path]/calibrate/[date] 
	have been processed by $chkarrcal.py every time before execute below program.

1. $chkarrimg.py

	This code will first mark bad images with X_*_X,
	and then arrange your images in current folder.
	$mv them into different folder by object, band, and exptime.
	find proper dark and flat automatically, then do subtraction of dark and division of flat.

	you should execute this code in [source path]/image/[date] or you will ruin your data.

2. $fit_move.py list_divFLAT
	
	list_divFLAT: 
	A list contain the name of images you want to processed. 
	It will generated automatically by $chkarrimg.py
	
	This code will find reference form [path of result]/reference
	If no proper reference, Ths first name in list_divFLAT will be reference.
	and all images following will match the position of reference.
	
	only execute in [source path]/image/[date]/[object]/[band and exptime]

3. $ls *_m.fits > list_m
	
	list_m:
	a list contain the name of matched images you want to process.
	
	This command will generate list_m we will use below.

	execute in the same path above 

4. $fit_stack.py mdn list_m

	mdn: 
	This is stack option, mdn means median.
	
	list_m:
	a list contain the name of matched images you want to process.
	This should be process in previous step.
	
	This command will generate a stacked image of all match images in list_m, 
	saved in current folder.
	
	execute in the same path above

5. upload stacked file to nova.astrometry.net, in order to access the wcs.

6. $wgetastro.py [job number] [saved filename]

	job number : 
	This number will be display on result page of nova.astrometry.net
	copy and paste here.

	saved filename:
	The name you want to name the downloading file.
	
	This command will download image from nova.astrometry.net
	This image is stacked image, which generated in step 4, with wcs.

7. $get_mag [ecc] [band] [filename]

	ecc : 
	eccentricity of stars, default is 1.

	band : 
	band of filter, there are options: U, B, V, R, I, N.

	filename : 
	The file you want to work with.
	
	This command will findout the delta_m of this image with other online star catalog.

8. $get_all_star.py [filename]

	filename :
        The file you want to work with.
	
	This command will findout stars in this images, 
	and save raw star catalog in [path of result]/TAT_raw_star_catalog

9. $get_noise.py [unit] [method] list_m

	This step could be executed before step 7 and 8.
	
	unit :
	The unit of brightness.
	There are two available option, "mag" and "count".
	recommand "mag".
	
	method :
	The method you used for stacking image.
	There are two available option, "mdn" and "mean".
	recommand "mdn".

	This command will find the formula with variable time and magnitude.
