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
20181205 version alpha 3
    1. Add a new func for updating photometry results.
'''
import mysql.connector as mariadb
import time
import numpy as np
from TAT_env import src_tb_name, src_titles, src_format, \
                    obs_data_tb_name, obs_data_titles, obs_data_format, \
                    trg_tb_name, trg_format, \
                    df_tb_name, df_format, \
                    ctn_tb_name, ctn_format 
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
        cursor.execute("insert into {0} ({1}) values ({2})".format( obs_data_tb_name,  
                    ', '.join(obs_data_titles[1:]), ', '.join(['%s'] * len(obs_data_titles[1:]))), 
                    tuple(source[1:]))
    if new:
        for source in new_sources:
            cursor.execute("insert into {0} ( {1} ) values ({2})".format( src_tb_name, 
                        ', '.join(src_titles[1:]), ', '.join(['%s'] * len(src_titles[1:]))), 
                        tuple(source))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

# save or append data to sql database.
def save2sql_EP(correlated_data, ID):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # create data base if not exist
    create_TAT_tables()
    # Save data into the table in the database.
    for i in range(len(correlated_data)):
        cursor.execute("UPDATE `{0}` SET `EP_MAG` = '{1}' WHERE `ID` = {2}".format(obs_data_tb_name, correlated_data[i,1], ID[i]))
        cursor.execute("UPDATE `{0}` SET `E_EP_MAG` = '{1}' WHERE `ID` = {2}".format(obs_data_tb_name, correlated_data[i,2], ID[i]))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

# save or append data to sql database.
def save2sql_CATA(correlated_data, ID):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # create data base if not exist
    create_TAT_tables()
    # Save data into the table in the database.
    for i in range(len(correlated_data)):
        cursor.execute("UPDATE `{0}` SET `CATA_MAG` = '{1}' WHERE `ID` = {2}".format(obs_data_tb_name, correlated_data[i,0], ID[i]))
        cursor.execute("UPDATE `{0}` SET `E_CATA_MAG` = '{1}' WHERE `ID` = {2}".format(obs_data_tb_name, correlated_data[i,1], ID[i]))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def create_TAT_tables():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # Create table `observation_data`, which save the data getting from image. 
    sql = 'create table if not exists `{0}` ({1})'.format(obs_data_tb_name, ', '.join(obs_data_format))
    cursor.execute(sql)
    # Create table `source` saving the detected sources on images.
    sql = 'create table if not exists `{0}` ({1})'.format(src_tb_name, ', '.join(src_format))
    cursor.execute(sql)
    #-----------------------------------------
    # Inherit from Yun-Yan
    # Create table `targets` saving the basic infomation of targets.
    sql = 'create table if not exists `{0}` ({1})'.format(trg_tb_name, ', '.join(trg_format))
    cursor.execute(sql)
    # Create table `data_file` saving the fundamental properties of images.
    sql = 'create table if not exists `{0}` ({1})'.format(df_tb_name, ', '.join(df_format))
    cursor.execute(sql)
    # Create table `container` saving where the images saved have been processed already.`
    sql = 'create table if not exists `{0}` ({1})'.format(ctn_tb_name, ', '.join(ctn_format))
    cursor.execute(sql)
    #-----------------------------------------
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def remove_TAT_tables():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # remove table `observation_data` and `source_name`
    sql = 'drop table {0}'.format(obs_data_tb_name)
    cursor.execute(sql)
    sql = 'drop table {0}'.format(src_tb_name)
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def find_source_match_coords(ra = np.nan, dec = np.nan, margin = 0.0):
    # Check the validation of the ra and dec
    if np.isnan(ra) or np.isnan(dec):
        print ("please specifiy the ra and dec.")
        return None
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # Load data from table
    cursor.execute('select * from TAT.{0} \
                    where ((RA between {1} and {2}) or (RA between {3} and {4}) or (RA between {5} and {6})) \
                    and (`DEC` between {7} and {8})'.format(src_tb_name, 
                                                            ra - margin, ra + margin, 
                                                            ra - 360 - margin, ra - 360 + margin,
                                                            ra + 360 - margin, ra + 360 + margin,
                                                            dec - margin, dec + margin))
    data = cursor.fetchall()
    cursor.close()
    cnx.close()
    return data

def find_fileID(file_name):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    cursor.execute("select ID from TAT.data_file where FILENAME='{0}'".format(file_name))
    data = cursor.fetchall()
    data = np.array(data, dtype = int).flatten()
    ans = data[0]
    cursor.close()
    cnx.close()
    return ans
