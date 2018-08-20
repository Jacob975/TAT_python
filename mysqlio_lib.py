#!/usr/bin/python
'''
Program:
    This is a program providing the way to save table in mysql. 
Usage: 
    Add this line in your python program:
    import mysqlio_lib
Editor:
    Jacob975
20180820
#################################
update log
20180820 version alpha 1
    1. The code works.
'''
import mysql.connector as mariadb
import time
import numpy as np
from TAT_env import source_db_format
from TAT_env import table_titles 
from sys import argv

def save2sql(db_name, table_name, data, unique_jd = False):    
    #----------------------------------------
    # Login mariadb as user 'TAT'@'localhost'
    authority = {   'user':'TAT',         
                    'password':'1234',        
                    'database':db_name, 
                    'host':'localhost'
                }
    cnx = mariadb.connect(**authority)
    cursor = cnx.cursor()
    # Create a table in database
    sql = 'create table if not exists `{0}` ({1})'.format(table_name, ', '.join(source_db_format))
    cursor.execute(sql)
    # Save data into the table in the database.
    if unique_jd:
        for source in data:
            # TBA
            cursor.execute("insert into `{0}` ({1}) values ({2})".format( table_name, ', '.join(table_titles[1:]), ', '.join(['%s'] * len(table_titles[1:]))), tuple(source[1:]))
    if not unique_jd:
        for source in data:
            cursor.execute("insert into `{0}` ({1}) values ({2})".format( table_name, ', '.join(table_titles[1:]), ', '.join(['%s'] * len(table_titles[1:]))), tuple(source[1:]))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def load_from_sql(db_name, table_name):
    #----------------------------------------
    # Login mariadb as user 'TAT'@'localhost'
    authority = {   'user':'TAT',         
                    'password':'1234',        
                    'database':db_name, 
                    'host':'localhost'
                }
    cnx = mariadb.connect(**authority)
    cursor = cnx.cursor()
    # Load data from table
    cursor.execute('select * from `{0}`'.format(table_name))
    data = cursor.fetchall()
    data = np.array(data)
    return data
