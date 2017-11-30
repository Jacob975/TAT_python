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
path_of_source = "/mazu/users/Jacob975"

#--------------- Setting code path ------------------
# code path means where do you install these code about tat.
# recommand: /home/username/bin/tat_python
path_of_code = "/home/Jacob975/bin/tat_python"

#--------------- Setting result path ----------------
# result path means once you produce some data by tat_python.
# result path will be where to save.
# recommand: /home/tat_result
path_of_result = "/home/Jacob975/demo"
