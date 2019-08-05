#!/usr/bin/python
'''
Program:
    This is a program for setting up databases for TAT data.
Usage: 
    db_setup.py [option]
Editor:
    Jacob975
20180822
#################################
update log
20180822 version alpha 1
    1. The code works.
20180919 version alpha 2
    1. Add a new option for reset TAT databases.
'''
import numpy as np
import time
from sys import argv
import mysqlio_lib
import TAT_env
#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load arguments.
    if len(argv) != 2:
        print "Error! The number of arguments is wrong."
        print "Usage: db_setup.py [option]"
        print "Available options: create, recreate, recreate_{0}, recreate_{1}, recreate_{2}, recreate_{3}."\
                .format(TAT_env.obs_data_tb_name,
                        TAT_env.src_tb_name,
                        TAT_env.im_tb_name,
                        TAT_env.ctn_tb_name)
        exit()
    option = argv[1]
    #----------------------------------------
    # Run
    if option == 'create':
        mysqlio_lib.create_TAT_tables()    
    elif option == 'recreate':
        mysqlio_lib.remove_TAT_tables()
        mysqlio_lib.create_TAT_tables()
    elif option == 'recreate_{0}'.format(TAT_env.obs_data_tb_name):
        mysqlio_lib.remove_obs_data_table()
        mysqlio_lib.create_TAT_tables()
    elif option == 'recreate_{0}'.format(TAT_env.src_tb_name):
        mysqlio_lib.remove_src_data_table()
        mysqlio_lib.create_TAT_tables()
    elif option == 'recreate_{0}'.format(TAT_env.im_tb_name):
        mysqlio_lib.remove_im_data_table()
        mysqlio_lib.create_TAT_tables()
    elif option == 'recreate_{0}'.format(TAT_env.ctn_tb_name):
        mysqlio_lib.remove_epoch_table()
        mysqlio_lib.create_TAT_tables()
    else:
        print 'Wrong input option!'
        print "Available options: create, recreate."
        exit()
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
