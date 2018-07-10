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
path_of_image = "/home2/TAT_test"

#--------------- Setting code path ------------------
# code path means where do you install these code about tat.
# recommand: /home/username/bin/tat_python
path_of_code = "/home/tat/TAT_programs/TAT_image_reduction"

#--------------- Name of Folders---------------------
catalog_dir = "tat_catalog"

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
                {'RA':'20:12:7', 'DEC':'38:21:18', 'name':'NGC6888'}]

#--------------- band list-------------------------
band_list = ["A", "B", "C", "N", "R", "V" ]
#--------------- site list-------------------------
site_list = ["TF", "KU"]
#--------------- type list-------------------------
type_list = ["data", "dark", "flat"]
#--------------- FOV------------------------------
# 1 pixel is equal to 2.19 arcsec on TAT image.
pix1 = 2.2
