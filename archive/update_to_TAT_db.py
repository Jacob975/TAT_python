#!/usr/bin/python
'''
Program:
    This is a program that saving the basic information of each image we have.
Usage: 
    update_to_TAT_db.py 
Editor:
    Yun-Yan
    Jacob975
20190103
#################################
update log
20190103 version alpha 1:
    1. I (Jacob975) inherit the code from Yun-Yan's github.
'''
import MySQLdb                              #Let python use mysql
from astropy.io import fits as pyfits       #To get the header key, use pyfits
import os                                   #To use command in terminal
import sys                                  #Used in some error, we can exodus
from back_up_path import LOG, backuppath
import time
import numpy as np

def RA_to_deg(RA):
    RA_deg=0
    try:
        RA=RA.split(':')

        for i in range(len(RA)):
            RA[i]=float(RA[i])

        RA_deg=RA[0]*15.0+RA[1]*15.0/60.0+RA[2]*15.0/3600.0
    except:
        pass
    return RA_deg

def DEC_to_deg(DEC):
    DEC_deg=0
    try:
        DEC=DEC.split(':')

        for i in range(len(DEC)):
            DEC[i]=float(DEC[i])

        DEC_deg=DEC[0]+DEC[1]/60.0+DEC[2]/3600.0
    except:
        pass
    return DEC_deg


# The function to read the infos of images and save in Table `data_file`.
def insert_data_file(filename,path):

    name="{0}".format(filename)           # Set name as the filename. 
    header=pyfits.getheader(filename)     # Get the header from the fit file. 
    key=header.keys()                     # Read the variable key from header.   
    datakey=[]                            # Define the datakey as a list. 
    name="'{0}'".format(filename)         # Set name in mysql style. 


    # Connect the Mysql and use the user "TAT" .The form is (your localhost , username, password, name of database)
    db = MySQLdb.connect("localhost", "TAT" ,"1234","TAT")    
    cursor = db.cursor()                     # Create a Cursor object to execute queries. 


    # Describe the data_file 
    sql= "desc data_file;"                      
    try:
        cursor.execute(sql)
        results=cursor.fetchall()      # The result of the Mysql command "desc data_file"
        
        # We just need the first column of "desc data_file"( its meaning is the all key in table data_file)
        for row in results:
            datakey.append(row[0])     

        # Insert the filename
        sql="insert into data_file (FILENAME) values ({0});".format(name)
        try:
            cursor.execute(sql)         #excute the "isnert into data_file...."
            db.commit()                 #do nothing
        except:
            db.rollback()               #skip if error

        # Update the path
        sql="UPDATE data_file SET `FILEPATH` = '{0}' WHERE `FILENAME` = {1} ;".format(path,name)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        # Set false to "subbed" and "divfitted"  
        sql="UPDATE data_file set `SUBBED`  = False WHERE `FILENAME`= {0};".format(name)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

        sql="UPDATE data_file set `FLATDIVED`  = False WHERE `FILENAME`= {0};".format(name)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        
        for header_element in key:
            if header_element=="DEC":
                DECdeg = DEC_to_deg(header[header_element])
            if header_element=="RA":
                RAdeg = RA_to_deg(header[header_element])

        sql="UPDATE data_file set `DEC(deg)`  = '{0}' WHERE `FILENAME`= {1};".format(DECdeg,name)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        sql="UPDATE data_file set `RA(deg)`  = '{0}' WHERE `FILENAME`= {1};".format(RAdeg,name)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        
        #Match all key in header and data_file.
        for header_element in key:
            for data_element in datakey:
                if header_element==data_element:
                    if (type(header[data_element]) == bool) or (type(header[data_element]) == int) or (type(header[data_element]) == float):
                        sql="UPDATE data_file SET `{0}` = {1} WHERE `FILENAME` = {2} ;".format(data_element,header[header_element],name)
                    else:
                        sql="UPDATE data_file SET `{0}` = '{1}' WHERE `FILENAME` = {2} ;".format(data_element,header[header_element],name)
            if 'OBSERVAT'== header_element:
                sql="UPDATE data_file set `SITENAME`  = '{0}' WHERE `FILENAME`= {1};".format(header['OBSERVAT'],name)
            if 'LOCATION'== header_element:
                sql="UPDATE data_file set `SITENAME`  = '{0}' WHERE `FILENAME`= {1};".format(header['LOCATION'],name)
            try:
                cursor.execute(sql)
                db.commit()
            except:
                db.rollback()
    # if command "desc data_file" were wrong, it would output error
    except:
        print "Error: unable to fetch data"
 
    # Unconnect the Mysql
    db.close()
    return

def update_to_datafile_db(backuppath):
    # Read all file and directory under the given path
    # (root --> the current directory, directory --> all directory in the root and files --> all the file in the root)
    # If all files in the current directory are read, one of dirs become root and move on.
    for root, dirs, files in os.walk(backuppath):
        for name in dirs:
            # The current directory appends one of the sub directory.
            path=os.path.join(root, name)
            os.chdir(path)
            # Let all filename contain the fit be a file, and let the filename line by line.
            os.system("ls *.fit* > list.txt")
            image_name_list = np.loadtxt('list.txt', dtype = str)
            for name in image_name_list:
                # Use the function insert_data_file one by one.
                insert_data_file(name, path)
            # After inserting the database TAT, delete the name list. 
            os.remove("list.txt")  
            print(path,"ok")
    return 0

#-------------------------------------------------
# Main process 
if __name__ =="__main__":
    # Measure time
    start_time = time.time()
    #--------------------------------------------
    failure = update_to_datafile_db(backuppath)
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
