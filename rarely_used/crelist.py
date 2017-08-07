#!/usr/bin/python
'''
Program:
THis is a program used to create a series
method: $ crelist.py [ini number] [fin number]
ini number : initial number, which should be a integer, smaller than fin number.
fin number : final number, which should be a integer.
editor Jacob975
20170118 version beta 1
################################
update log

alpha 1:    20170118:
    the program can run properly, but no alias and explaination.

beta 1:     20170118:
    the program con run, include alias and explaination.
    The program cannot detect the input type neither prevent itself from tpye error.
'''
from sys import argv

ini_number= argv[1]
fin_number= argv[2]

print 'Computer will create a file named "series_number", include interger'
print 'from '+ini_number+'to '+fin_number

length=int(fin_number)-int(ini_number)+1

file = open('series_number','w')
for i in range(length):
    temp=str(int(ini_number)+i)+"\n"
    file.write(temp)
file.close()
