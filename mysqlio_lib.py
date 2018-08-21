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

def TAT_auth(db_name):
    # Login mariadb as user 'TAT'@'localhost'
    authority = {   'user':'TAT',         
                    'password':'1234',        
                    'database':db_name, 
                    'host':'localhost'
                }
    cnx = mariadb.connect(**authority)
    return cnx

# save or append data to sql database.
def save2sql(db_name, table_name, data, unique_jd = False):    
    cnx = TAT_auth(db_name)
    cursor = cnx.cursor()
    # Create a table in database
    sql = 'create table if not exists `{0}` ({1})'.format(table_name, ', '.join(source_db_format))
    cursor.execute(sql)
    # Save data into the table in the database.
    if unique_jd:
        for source in data:
            # load a list of julian date
            cursor.execute("select JD from `{0}`".format(table_name))
            new_jd = float(source[-2])
            jd_array = np.array(cursor.fetchall(), dtype = float).flatten()
            # if julian date are not duplicated, save the new detection.
            index_repeat_jd = np.where(jd_array == new_jd)
            if len(index_repeat_jd[0]) == 0:
                cursor.execute("insert into `{0}` ({1}) values ({2})".format( table_name, ', '.join(table_titles[1:]), ', '.join(['%s'] * len(table_titles[1:]))), tuple(source[1:]))
    if not unique_jd:
        for source in data:
            cursor.execute("insert into `{0}` ({1}) values ({2})".format( table_name, ', '.join(table_titles[1:]), ', '.join(['%s'] * len(table_titles[1:]))), tuple(source[1:]))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

# Load a table from sql database
def load_from_sql(db_name, table_name):
    cnx = TAT_auth(db_name)
    cursor = cnx.cursor()
    # Load data from table
    cursor.execute('select * from `{0}`'.format(table_name))
    data = cursor.fetchall()
    data = np.array(data)
    cursor.close()
    cnx.close()
    return data

# This is a func for showing the name of tables in the database.
def show_tables(db_name):
    cnx = TAT_auth(db_name)
    cursor = cnx.cursor()
    cursor.execute('show tables')
    table_list = cursor.fetchall()
    table_array = np.array(table_list, dtype = str).flatten()
    cursor.close()
    cnx.close()
    return table_array
