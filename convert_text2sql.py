#!/usr/bin/python
'''
Program:
    This is a program for testing mysql connector package. 
Usage: 
    convert_text2sql.py [destinative database] [name of text file]
Editor:
    Jacob975
20180816
#################################
update log
20180816 version alpha 1
    1. The code works.
'''
import mysql.connector as mariadb
import time
import numpy as np
from TAT_env import source_db_format
from TAT_env import table_titles 
from sys import argv

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    if len(argv) != 3:
        print ("Wrong the number of arguments.")
        print ("Usage: convert_text2sql.py [destinative database] [name of text file]")
        exit()
    db_name = argv[1]
    table_name = argv[2]   
    #----------------------------------------
    # Load the table and login the database
    table = np.loadtxt(table_name, dtype = object, skiprows = 1)
    # Login mariadb as user 'TAT'@'localhost'
    authority = {   'user':'TAT',         
                    'password':'1234',        
                    'database':db_name, 
                    'host':'localhost'
                }
    cnx = mariadb.connect(**authority)
    cursor = cnx.cursor()
    # Create a table in database, try to read and write.
    sql = 'create table if not exists `{0}` ({1})'.format(table_name[:-4], ', '.join(source_db_format))
    cursor.execute(sql)
    # Save data into the table in the database.
    for source in table:
        cursor.execute("insert into `{0}` ({1}) values ({2})".format( table_name[:-4], ', '.join(table_titles[1:]), ', '.join(['%s'] * len(table_titles[1:]))), tuple(source[1:]))
    # Show data
    cursor.execute('select * from `{0}`'.format(table_name[:-4]))
    data = cursor.fetchall()
    print data
    # Make sure data is committed to the database
    cnx.commit()
    cursor.close()
    cnx.close()
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
