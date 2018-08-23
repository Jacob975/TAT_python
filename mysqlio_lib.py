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
20180822 version alpha 2
    1. update some names of variables
'''
import mysql.connector as mariadb
import time
import numpy as np
from TAT_env import src_name_tb_name, src_name_titles, src_name_format, obs_data_tb_name, obs_data_titles, obs_data_format 
from sys import argv

def TAT_auth():
    # Login mariadb as user 'TAT'@'localhost'
    authority = {   'user':'TAT',         
                    'password':'1234',        
                    'database':'TAT', 
                    'host':'localhost'
                }
    cnx = mariadb.connect(**authority)
    return cnx

# save or append data to sql database.
def save2sql(data, new_sources = None, new = None):    
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # create data base if not exist
    create_TAT_tables()
    # Save data into the table in the database.
    for source in data:
        cursor.execute("insert into {0} ({1}) values ({2})".format( obs_data_tb_name, ', '.join(obs_data_titles[1:]), ', '.join(['%s'] * len(obs_data_titles[1:]))), tuple(source[1:]))
    if new != None:
        for source in new_sources:
            cursor.execute("insert into {0} ( `name` ) values ( '{1}' )".format( src_name_tb_name, source))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def create_TAT_tables():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # create table `observation_data` and `source_name`
    sql = 'create table if not exists `{0}` ({1})'.format(obs_data_tb_name, ', '.join(obs_data_format))
    cursor.execute(sql)
    sql = 'create table if not exists `{0}` ({1})'.format(src_name_tb_name, ', '.join(src_name_format))
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

# Load a table from sql database
def load_src_name_from_db():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # Load data from table
    cursor.execute('select name from {0}'.format(src_name_tb_name))
    data = cursor.fetchall()
    data = np.array(data).flatten()
    cursor.close()
    cnx.close()
    return data
