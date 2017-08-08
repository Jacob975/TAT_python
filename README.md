# tat_python
Program for sorting and processing images of TAT telescope

#Setup
1. $vim tat_config

	set path in tat_config

2. $vim tat_datactrl.py

	set path of tat_config in tat_datactrl.get_path

3. $setup_tat_folder.py

	This code will set up all folder you need, Haven't been composed.

#Below are standard steps of processing TAT data.

0. $chkarrcal.py
	
	you should check all calibrate you have in [source path]/calibrate/[date] 
	have been processed by $chkarrcal.py every time before execute below program.

1. $chkarrimg.py

	you should execute this code in [source path]/image/[date] or you will ruin your data.

2. $fit_move.py list_divFLAT
	
	only execute in [source path]/image/[date]/[object]/[band and exptime]

3. $ls *_m.fits > list_m

	execute in the same path above 

4. $fit_stack.py mdn list_m

	execute in the same path above

5. upload stacked file to nova.astrometry.net, in order to access the wcs.

6. $wgetastro.py [job number] [saved filename]

	job number : 
	This number will be display on result page of nova.astrometry.net
	copy and paste here.

	saved filename:
	The name you want to name the downloading file.

7. $get_mag [ecc] [band] [filename]

	ecc : 
	eccentricity of stars, default is 1.

	band : 
	band of filter, there are options: U, B, V, R, I, N.

	filename : 
	The file you want to work with.

8. $get_all_star.py [filename]

	filename :
        The file you want to work with.

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

