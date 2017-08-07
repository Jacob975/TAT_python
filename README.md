# tat_python
Program for sorting and processing images of TAT telescope

Step.
1. chkarrimg.py
2. fit_move.py list_divFLAT
3. ls *_m.fits > list_m
4. fit_stack.py mdn list_m
5. upload stacked file to nova.astrometry.net, in order to access the wcs.
6. wgetastro.py [job number] [saved filename]

	job number : 
	This number will be display on result page of nova.astrometry.net
	copy and paste here.

	saved filename:
	The name you want to name the downloading file.

7. get_mag [ecc] [band] [filename]

	ecc : 
	eccentricity of stars, default is 1.

	band : 
	band of filter, there are options: A, B, C, V, R, N.

	filename : 
	The file you want to work with.

8. get_all_star.py [filename]
	
	filename :
        The file you want to work with.

9. get_noise.py mag mdn list_m

