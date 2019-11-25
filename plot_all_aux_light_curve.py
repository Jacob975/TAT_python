# !/usr/bin/python
import numpy as np
import os


class option_plot_auxLC():
    def __init__(self):
        self.opts = None
    def create(self):
        s = [   '# Where to get data',
                '# 1: from given filename, and the name become the filename.',
                '# 2: from database, and the name become the target name',
                where_they_from,
                '# name',
                '# The name of auxiliary star or the name of files',
                data_name,
                '# Start date in YYYYMMDD',
                '# The first date of the plot showing.',
                '# "skip" will make the program shows all light curves.',
                start_date,
                '# End date in YYYYMMDD',
                '# The last date of the plot showing.',
                '# "skip" will make the program shows all light curves.',
                end_date,
                '# Band',
                '# Available options: N, C, A, V, B, R',
                band,
                '# Exptime',
                '# The exposure time of selected images',
                exptime
                ]
        obj_n = data_name
        np.savetxt('option_plot_auxLC'+obj_n+'.txt', s, fmt = '%s')
    def load(self, file_name):
        self.opts = np.loadtxt(file_name, dtype = str)
        self.opts = list(self.opts)
        return self.opts



if __name__ == "__main__":
    # Measure time
    start_time = time.time()
    #----------------------------------------
    # Load argv
    stu = option_plot_auxLC()
    if len(argv) != 2:
        print 'The number of arguments is wrong.'
        print 'Usage: plot_aux_light_curve.py [option_file]'
        stu.create()
        exit()
    options = argv[1]
    where_they_from,\
    data_name,\
    start_date,\
    end_date,\
    band,\
    exptime, = stu.load(options)
    where_they_from = int(where_they_from)



for obj_n in obj_li:
    o.system('python plot_aux_light_curve.py option_plot_auxLC'+obj_n+'.txt')


















