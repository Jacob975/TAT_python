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
import TAT_env
from TAT_env import src_tb_name, src_titles, src_format, \
                    obs_data_tb_name, obs_data_titles, obs_data_format, \
                    trg_tb_name, trg_format, \
                    im_tb_name, im_format, \
                    ctn_tb_name, ctn_format 
from astropy.io import fits as pyfits
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
    # Check if the source exist.
    cursor.execute( "select * from {0} where `NAME` = '{1}'".format(
                    obs_data_tb_name,
                    source))
    tmp = cursor.fetchall()
    if len(tmp) == 0:
        save2sql_container(name)

    # Save data into the table in the database.
    for source in data:
        # Check if the detection saved before.
        cursor.execute( "select * from {0} where `NAME` = '{1}' and `BJD` = '{2}'".format(
                        obs_data_tb_name,
                        # NAME, BJD
                        source[1], source[3]))
        tmp = cursor.fetchall()
        # If no, save it.
        if len(tmp) == 0:
            cursor.execute("insert into {0} ({1}) values ({2})".format( obs_data_tb_name,  
                                                                        ', '.join(obs_data_titles[1:]), 
                                                                        ', '.join(['%s'] * len(obs_data_titles[1:]))), 
                            tuple(source[1:]))
            cnx.commit()
        # If do, skip it.
        else:
            continue
    if new:
        for source in new_sources:
            cursor.execute("insert into {0} ( {1} ) values ({2})".format( src_tb_name, 
                                                                        ', '.join(src_titles[1:]), 
                                                                        ', '.join(['%s'] * len(src_titles[1:]))), 
                            tuple(source))
            cnx.commit()
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

def save2sql_images(name, path):
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # create data base if not exist
    create_TAT_tables()
    try:
        header=pyfits.getheader(name)       # Get the header from the fit file. 
    except:
        return 1
    key=header.keys()                   # Read the variable key from header.   
    datakey=[]                          # Define the datakey as a list. 

    # Describe the images, the table. 
    try:
        sql= "desc {0}".format(im_tb_name)                      
        cursor.execute(sql)
        results=cursor.fetchall()      # The result of the Mysql command "desc images"
    # if command "desc images" were wrong, it would output error
    except:
        print "Error: unable to fetch data"
        return 1
    
    # We just need the first column of "desc images"
    # Its meaning is the all key in the  table, images.
    for row in results:
        datakey.append(row[0])     

    # Insert the filename
    sql="insert into {0} (`FILENAME`) values ('{1}');".format(
        im_tb_name, 
        name)
    try:
        cursor.execute(sql)         #excute the "isnert into images...."
        cnx.commit()                #do nothing
    except:
        cnx.rollback()              #skip if error

    # Update the path
    sql="UPDATE {0} SET `FILEPATH` = '{1}' WHERE `FILENAME` = '{2}' ;".format(
        im_tb_name, 
        path,
        name)
    try:
        cursor.execute(sql)
        cnx.commit()
    except:
        cnx.rollback()

    # Set false to "subbed" and "divfitted"  
    sql="UPDATE {0} set `SUBBED`  = False WHERE `FILENAME`= '{1}';".format(
        im_tb_name,
        name)
    try:
        cursor.execute(sql)
        cnx.commit()
    except:
        cnx.rollback()

    sql="UPDATE {0} set `FLATDIVED`  = False WHERE `FILENAME`= '{1}';".format(
        im_tb_name, 
        name)
    try:
        cursor.execute(sql)
        cnx.commit()
    except:
        cnx.rollback()

    # Update the coordinate, R.A. and Dec.
    try:
        coord = SkyCoord(header["RA"]+" "+header["DEC"], unit=(u.hourangle, u.deg))
    except:
        pass
    else:
        sql="UPDATE {0} set `DEC(deg)`  = '{1}' WHERE `FILENAME`= '{2}';".format(
            im_tb_name,
            coord.dec.degree,
            name)
        try:
            cursor.execute(sql)
            cnx.commit()
        except:
            cnx.rollback()
        sql="UPDATE {0} set `RA(deg)`  = '{1}' WHERE `FILENAME`= '{2}';".format(
            im_tb_name, 
            coord.ra.degree,
            name)
        try:
            cursor.execute(sql)
            cnx.commit()
        except:
            cnx.rollback()
    
    # Match all key in header and the table, images.
    for header_element in key:
        for data_element in datakey:
            if header_element==data_element:
                if (type(header[data_element]) == bool) \
                    or (type(header[data_element]) == int) \
                    or (type(header[data_element]) == float):
                    sql="UPDATE {0} SET `{1}` = {2} WHERE `FILENAME` = '{3}' ;".format(
                        im_tb_name, 
                        data_element,
                        header[header_element],
                        name)
                else:
                    sql="UPDATE {0} SET `{1}` = '{2}' WHERE `FILENAME` = '{3}' ;".format(
                        im_tb_name,
                        data_element,
                        header[header_element],
                        name)
        if 'OBSERVAT'== header_element:
            sql="UPDATE {0} set `SITENAME`  = '{1}' WHERE `FILENAME`= '{2}';".format(
                im_tb_name,
                header['OBSERVAT'],
                name)
        if 'LOCATION'== header_element:
            sql="UPDATE {0} set `SITENAME`  = '{1}' WHERE `FILENAME`= '{2}';".format(
                im_tb_name,
                header['LOCATION'],
                name)
        try:
            cursor.execute(sql)
            cnx.commit()
        except:
            cnx.rollback()
    # Make sure data is committed to the database.
    cursor.close()
    cnx.close()
    return 0

def save2sql_container(name):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # create data base if not exist
    create_TAT_tables()
    # Save data into the table in the database.
    cursor.execute("INSERT INTO {0} (`NAME`) VALUES ('{1}')".format( ctn_tb_name, name))
    # Make sure data is committed to the database.
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def update2sql_container(   name, 
                            stat, 
                            comment, 
                            append = False):
    cnx = TAT_auth()
    cursor = cnx.cursor()
    # create data base if not exist
    create_TAT_tables()
    # Check if this container exist
    cursor.execute( "select * from {0} where `NAME` = '{1}'".format(
                    ctn_tb_name,
                    name))
    tmp = cursor.fetchall()
    if len(tmp) == 0:
        save2sql_container(name)
    actual_comment = comment
    if append:
        cursor.execute("select `COMMENT` from {0} where `NAME` = '{1}'".format(ctn_tb_name, name))
        last_comment = cursor.fetchall()
        try:
            actual_comment = '{0}{1}'.format(   last_comment[0][0], 
                                                comment)
        except:
            print last_comment
            actual_comment = comment
        cnx.commit()
    # Save data into the table in the database.
    cursor.execute( "UPDATE {0} set `STATUS` = '{1}' where `NAME` = '{2}'".format( 
                    ctn_tb_name, 
                    stat,
                    name))
    cursor.execute( "UPDATE {0} set `COMMENT` = '{1}' where `NAME` = '{2}'".format( 
                    ctn_tb_name, 
                    actual_comment,
                    name))
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
    # Create table `images` saving the fundamental properties of images.
    sql = 'create table if not exists `{0}` ({1})'.format(im_tb_name, ', '.join(im_format))
    cursor.execute(sql)
    # Create table `container` saving where the images saved have been processed already.`
    sql = 'create table if not exists `{0}` ({1})'.format(ctn_tb_name, ', '.join(ctn_format))
    cursor.execute(sql)
    # Create table `observatory` saving the site of TAT. 
    sql = 'create table if not exists `{0}` ({1})'.format(TAT_env.site_tb_name, ', '.join(TAT_env.site_format))
    cursor.execute(sql)
    #-----------------------------------------
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def remove_obs_data_table():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    sql = 'drop table {0}'.format(obs_data_tb_name)
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def remove_src_data_table():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    sql = 'drop table {0}'.format(src_tb_name)
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def remove_im_table():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    sql = 'drop table {0}'.format(im_tb_name)
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def remove_epoch_table():
    cnx = TAT_auth()
    cursor = cnx.cursor()
    sql = 'drop table {0}'.format(ctn_tb_name)
    cursor.execute(sql)
    cnx.commit()
    cursor.close()
    cnx.close()
    return 0

def remove_TAT_tables():
    remove_obs_data_table()
    remove_src_data_table()
    remove_im_table()
    remove_epoch_table()
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
    cursor.execute("select ID from {0} where FILENAME='{1}'".format(
                    im_tb_name,
                    file_name))
    data = cursor.fetchall()
    data = np.array(data, dtype = int).flatten()
    ans = data[0]
    cursor.close()
    cnx.close()
    return ans
