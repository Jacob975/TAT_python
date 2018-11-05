#!/usr/bin/python
'''
Program:
This is a table of environment variable of TAT python.
Usage:

    import TAT_env.py       // in your TAT python program

editor Jacob975
20171114
#################################
update log
20171114 version alpha 1:
    1. The first sight of table of environment table
20171130 version alpha 2:
    2. the path of source on zeus is moved from /brick to /mazu.
20180625 version alpha 3:
    1. Path of result is removed
20180820 version alpha 4:
    1. Add a source DB format
'''

# Comment of what kinds of variables are saved here.

#--------------- Setting python path ----------------
# python path is where you install python
# tat python can run under both python and python2
# please check the path by $which python python2
path_of_python = "/usr/bin/python"

#--------------- Setting source path ----------------
# source path means where will you put your row image.
# recommand: /home/username
path_of_image = "/home2/TAT_test/raw"

#--------------- Setting code path ------------------
# code path means where do you install these code about tat.
# recommand: /home/username/bin/tat_python
path_of_code = "/home2/TAT/programs/TATIRP"

#--------------- Name of Folders---------------------
path_of_result = "/home2/TAT_test/reduction"

#--------------- Object list---------------------------------
# every object recorded below will be read
object_list = [ {'RA':'21:53:24','DEC':'47:16:00','name':'IC5146'},
                {'RA':'03:29:10','DEC':'31:21:57','name':'NGC1333A'},
                {'RA':'12:55:38','DEC':'25:53:31','name':'WD1253+261'},
                {'RA':'18:36:57','DEC':'-28:55:42','name':'SgrNova'},
                {'RA':'19:20:30','DEC':'11:02:01','name':'HH32'},
                {'RA':'08:22:27','DEC':'13:44:07','name':'KELT-17'},
                {'RA':'11:52:58.8','DEC':'37:43:07.2','name':'Groombridge1830'},
                {'RA':'20:06:15', 'DEC':'44:27:24', 'name': 'KIC8462852'},
                {'RA':'21:29:58.42','DEC':'51:03:59.8','name':'PN'},
                {'RA':'21:06:53.9','DEC':'38:44:57.9','name':'61Cygni'},
                {'RA':'20:12:7', 'DEC':'38:21:18', 'name':'NGC6888'},
                # Kepler star
                {'RA':'21:00:06.19', 'DEC':'-05:05:39.85', 'name':'WASP-69b'}]

#--------------- Band list-------------------------
band_list = ["A", "B", "C", "N", "R", "V" ]
#--------------- Site list-------------------------
site_list = ["TF", "KU"]
#--------------- Type list-------------------------
type_list = ["data", "dark", "flat"]
#----------------Title for targets on Iraf table---
iraf_table_titles=[['id',         0 ],
                   ['xcentroid', 12 ],
                   ['ycentroid', 13 ],
                   ['fwhm',      14 ],
                   ['sharpness', 15 ],
                   ['roundness', 16 ],
                   ['pa',        17 ],
                   ['npix',      18 ],
                   ['sky',       19 ],
                   ['peak',      20 ],
                   ['flux',       4 ],
                   ['mag',        5 ]]

star_table_titles = [[  'id',           0],
                     [  'flux',         4],
                     [  'e_flux',       5],
                     [  'amplitude',    6],
                     [  'e_amplitude',  7],
                     [  'xcenter',      8],
                     [  'e_xcenter',    9],
                     [  'ycenter',     10],
                     [  'e_ycenter',   11],
                     [  'xsigma',      12],
                     [  'e_xsigma',    13],
                     [  'ysigma',      14],
                     [  'e_ysigma',    15],
                     [  'rot',         16],
                     [  'e_rot',       17],
                     [  'bkg',         18],
                     [  'e_bkg',       19],
                     [  'npix',        20]]

#------------- parameters for mysql table -----------------

src_name_tb_name = 'source_name'
obs_data_tb_name = 'observation_data'

src_name_titles = [ 'ID',
                    'NAME',]
src_name_format = [ 'ID INT AUTO_INCREMENT PRIMARY KEY',
                    '`NAME` VARCHAR(255)']

obs_data_titles = [ 'ID',               # unique object identification number. 
                    'NAME',
                    'ALIAS', 
                    'BJD',              # Barycentric Julian Time 
                    'FLUX',             
                    'INST_MAG',         # instrumental magnitude
                    'CATA_MAG',         # apparent magnitude copy from catalogu.e
                    'EP_MAG',           # apparent magnitude made by catalogue and Ensemble Photometry.
                    'IDP_MAG',          # apparent magnitdue made by catalogue and Improved method for Differenctial Photometry.
                    'RA',               
                    '`DEC`',              
                    'SP',               # Spectral tyep
                    'XCENTROID',        # object centroid.
                    'YCENTROID',        # object centroid.
                    'FWHM',             # full width of the half maximum.
                    'SHARPNESS',        # object sharpness.
                    'ROUNDNESS',        # object roundness based on marginal Gaussian fits.
                    'PA',               # polarization angle
                    'NPIX',             # number of pixels in the Gaussian kernel.
                    'SKY',              # background sky.
                    'PEAK',             # the peak, sky-subtracted, pixel value of the object.
                    'MJD', 
                    'JD', 
                    'HJD',
                    'FILEID', 
                    ]

obs_data_format = [ 'ID INT AUTO_INCREMENT PRIMARY KEY',
                    'NAME VARCHAR(255)',
                    'ALIAS VARCHAR(255)',
                    'BJD DOUBLE',              # Barycentric Julian Time 
                    'FLUX DOUBLE',             
                    'INST_MAG DOUBLE',         # instrumental magnitude
                    'CATA_MAG DOUBLE',         # apparent magnitude copy from catalogu.e
                    'EP_MAG DOUBLE',           # apparent magnitude made by catalogue and Ensemble Photometry.
                    'IDP_MAG DOUBLE',          # apparent magnitdue made by catalogue and Improved method for Differenctial Photometry.
                    'RA DOUBLE',
                    '`DEC` DOUBLE',             
                    'SP VARCHAR(255)',         # Spectral type
                    'XCENTROID DOUBLE',        # object centroid.
                    'YCENTROID DOUBLE',        # object centroid.
                    'FWHM DOUBLE',             # full width of the half maximum.
                    'SHARPNESS DOUBLE',        # object sharpness.
                    'ROUNDNESS DOUBLE',        # object roundness based on marginal Gaussian fits.
                    'PA DOUBLE',               # polarization angle
                    'NPIX DOUBLE',             # number of pixels in the Gaussian kernel.
                    'SKY DOUBLE',              # background sky.
                    'PEAK DOUBLE',             # the peak, sky-subtracted, pixel value of the object.
                    'MJD DOUBLE', 
                    'JD DOUBLE', 
                    'HJD DOUBLE',
                    'FILEID INT',
                    ]
#--------------- FOV------------------------------
# 1 pixel is equal to 2.19 arcsec on TAT image.
pix1 = 2.2

#--------------- URAT 1 --------------------------
URAT_1 = ['URAT1', 
          'RAJ2000', 
          'DEJ2000', 
          'Epoch', 
          'f.mag', 
          'e_f.mag', 
          'pmRA', 
          'pmDE', 
          'Jmag', 
          'Hmag', 
          'Kmag', 
          'Bmag', 
          'Vmag', 
          'gmag', 
          'rmag', 
          'imag']

index_URAT_1 = 'I/329'
#--------------- HIP -----------------------------
# Catalog I/196, a.k.a. Hipparcos Input Catalogue(HIC)
HIC =  ['HIC',
        'Comp',
        'RAJ2000', 
        'DEJ2000', 
        'Epoch', 
        'pmRA', 
        'pmDE', 
        'Hp',
        'Var',
        'Vmag',
        'B-V',
        'Sp',
        'Notes', 
        'HIP']

index_HIC = 'I/196'
