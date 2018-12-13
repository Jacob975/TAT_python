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
path_of_image = "/home2/TAT/data/raw"

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
                {'RA':'21:00:06.19', 'DEC':'-05:05:39.85', 'name':'WASP-69b'},
                # WASP
                {'RA':'08:46:19.29', 'DEC':'-08:01:37.01', 'name':'WASP-36'}]
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

star_table_titles = \
                    [[  'FLUX',         4],
                     [  'E_FLUX',       5],
                     [  'AMP',         17],
                     [  'E_AMP',       18],
                     [  'XCENTER',     19],
                     [  'E_XCENTER',   -1],
                     [  'YCENTER',     20],
                     [  'E_YCENTER',   -1],
                     [  'XSIGMA',      21],
                     [  'E_XSIGMA',    22],
                     [  'YSIGMA',      23],
                     [  'E_YSIGMA',    24],
                     [  'PA',          25],
                     [  'E_PA',        26],
                     [  'SKY',         27],
                     [  'E_SKY',       28],
                     [  'NPIX',        29]]

extend_star_table_titles = \
                    [[  'ID',           0],
                     [  'NAME',         1],
                     [  'ALIAS',        2],
                     [  'BJD',          3],
                     [  'FLUX',         4],
                     [  'E_FLUX',       5],
                     [  'INST_MAG',     6],
                     [  'E_INST_MAG',   7],
                     [  'CATA_MAG',     8],
                     [  'E_CATA_MAG',   9],
                     [  'EP_MAG',      10],
                     [  'E_EP_MAG',    11],
                     [  'IDP_MAG',     12],
                     [  'E_IDP_MAG',   13],
                     [  'RA',          14],
                     [  'DEC',         15],
                     [  'SP',          16],
                     [  'AMP',         17],
                     [  'E_AMP',       18],
                     [  'XCENTER',     19],
                     [  'YCENTER',     20],
                     [  'XSIGMA',      21],
                     [  'E_XSIGMA',    22],
                     [  'YSIGMA',      23],
                     [  'E_YSIGMA',    24],
                     [  'PA',          25],
                     [  'E_PA',        26],
                     [  'SKY',         27],
                     [  'E_SKY',       28],
                     [  'NPIX',        29],
                     [  'JD',          30],
                     [  'MJD',         31],
                     [  'HJD',         32],
                     [  'FILEID',      33]]

#------------- parameters for mysql table -----------------

src_tb_name = 'source'
obs_data_tb_name = 'observation_data'

src_titles = [ 'ID',
               'NAME',
               'RA',                # The right accension when the first time it shows up.
               '`DEC`']               # The declination when the first time it shows up.

src_format = [ 'ID INT AUTO_INCREMENT PRIMARY KEY',
               '`NAME` VARCHAR(255)',
               'RA DOUBLE',         # The right accension when the first time it shows up.
               '`DEC` DOUBLE']      # The declination when the first time it shows up.

obs_data_titles = \
                    [  'ID',        # unique object identification number. 
                       'NAME',      
                       'ALIAS',     
                       'BJD',       # Barycentric Julian Time
                       'FLUX',      
                       'E_FLUX',    
                       'INST_MAG',  # instrumental magnitude
                       'E_INST_MAG',
                       'CATA_MAG',  # apparent magnitude copy from catalogue
                       'E_CATA_MAG',
                       'EP_MAG',    # apparent magnitude made by catalogue and Ensemble Photometry.
                       'E_EP_MAG',  
                       'IDP_MAG',   # apparent magnitdue made by catalogue and Improved method for Differenctial Photometry.
                       'E_IDP_MAG', 
                       'RA',        
                       '`DEC`',       
                       'SP',        # Spectral type
                       'AMP',       # the peak, sky-subtracted, pixel value of the object.
                       'E_AMP',     
                       'XCENTER',   # object centroid.
                       'YCENTER',   # object centroid.
                       'XSIGMA',    
                       'E_XSIGMA',  
                       'YSIGMA',    
                       'E_YSIGMA',  
                       'PA',        
                       'E_PA',      
                       'SKY',       
                       'E_SKY',     
                       'NPIX',      # number of pixels in the Gaussian kernel.
                       'JD',        
                       'MJD',       
                       'HJD',       
                       'FILEID',]    

obs_data_format = \
                    [  'ID INT AUTO_INCREMENT PRIMARY KEY',        # unique object identification number. 
                       'NAME VARCHAR(255)',      
                       'ALIAS VARCHAR(255)',     
                       'BJD DOUBLE',       # Barycentric Julian Time
                       'FLUX DOUBLE',      
                       'E_FLUX DOUBLE',    
                       'INST_MAG DOUBLE',  # instrumental magnitude
                       'E_INST_MAG DOUBLE',
                       'CATA_MAG DOUBLE',  # apparent magnitude copy from catalogue
                       'E_CATA_MAG DOUBLE',
                       'EP_MAG DOUBLE',    # apparent magnitude made by catalogue and Ensemble Photometry.
                       'E_EP_MAG DOUBLE',  
                       'IDP_MAG DOUBLE',   # apparent magnitdue made by catalogue and Improved method for Differenctial Photometry.
                       'E_IDP_MAG DOUBLE', 
                       'RA DOUBLE',        
                       '`DEC` DOUBLE',       
                       'SP DOUBLE',        # Spectral type
                       'AMP DOUBLE',       # the peak, sky-subtracted, pixel value of the object.
                       'E_AMP DOUBLE',     
                       'XCENTER DOUBLE',   # object centroid.
                       'YCENTER DOUBLE',   # object centroid.
                       'XSIGMA DOUBLE',    
                       'E_XSIGMA DOUBLE',  
                       'YSIGMA DOUBLE',    
                       'E_YSIGMA DOUBLE',  
                       'PA DOUBLE',        
                       'E_PA DOUBLE',      
                       'SKY DOUBLE',       
                       'E_SKY DOUBLE',     
                       'NPIX DOUBLE',      # number of pixels in the Gaussian kernel.
                       'JD DOUBLE',        
                       'MJD DOUBLE',       
                       'HJD DOUBLE',       
                       'FILEID INT',]    

#--------------- FOV------------------------------
# 1 pixel is equal to 2.478 arcsec on TAT image.
pix1 = 2.478

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
