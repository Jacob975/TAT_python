#!/usr/bin/python
'''
Program:
    This is a program for testing mysql connector package. 
Usage: 
    test_mysql_connector.py
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

#--------------------------------------------
# main code
if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # define table format
    authority = {'user':'TAT',         
                'password':'1234',        
                'database':'frame_data', 
                'host':'localhost'
                }
    source_format = ['id INT AUTO_INCREMENT',
                     'name VARCHAR(255)', 
                     'address VARCHAR(255)',
                     'PRIMARY KEY (id)']
    # Login mariadb as user 'TAT'@'localhost'
    cnx = mariadb.connect(**authority)
    cursor = cnx.cursor()
    # Create a table in database, try to read and write.
    sql = 'create table if not exists test ({0})'.format(' , '.join(source_format))
    print sql
    cursor.execute(sql)
    cursor.execute('insert into test (name, address) values (%s, %s)', ("Alice", "46804804"))
    cursor.execute('insert into test (name, address) values (%s, %s)', ("Bob", "46804805"))
    cursor.execute('select * from test')
    data = cursor.fetchall()
    print data
    # drop the table
    cursor.execute('drop table test')
    cursor.execute('show tables')
    #---------------------------------------
    # Measure time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
