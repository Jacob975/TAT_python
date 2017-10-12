#!/usr/bin/python
'''
Program:
This is a program to code to apertrue photometry and psf photometry.
Currently, because psf phot haven't been done, option of psf photometry isn't available.

Usage:
1. tat_phot.py [image]

example:
    tat_phot.py image.fits      # star catalog and region of this image will be generated.

editor Jacob975
20170927
#################################
update log

20170927 version alpha 1
    apertrue part work well.

20170928 version alpha 2
    add specification of psf photometry

20170929 version alpha 3
    add specification of wcs controller

20171004 version alpha 4
    1. wcs controller is done, haven't been tested.

20171012 version alpha 5
    1. wcs controller is tested.
'''
from sys import argv
from photutils.detection import IRAFStarFinder, DAOStarFinder
from astropy.stats import gaussian_sigma_to_fwhm
from curvefit import hist_gaussian_fitting, get_peak_filter, get_star, get_star_unit, get_star_title, get_rid_of_exotic_vector, unit_converter
from astropy.table import Table, Column
from tat_datactrl import readfile, get_path
import numpy as np
import pyfits
import pywcs
import time
import warnings

# This is used to control argus.
class argv_controller:
    fits_list = []
    def __init__(self, argu):
        self.fits_list = self.get_fitsname(argu[-1])
        return
    def get_fitsname(self, name):
        name_list = name.split(".")
        if name_list[-1] == "fits" or name_list[-1] == "fit":
            fits_list = [name]
        else:
            fits_list=tat_datactrl.readfile(name)
        return fits_list

# This class is for finding basic paras of image.
class parameter:
    data = None
    bkg = 0.0
    std = 0.0
    sigma = 0.0
    date = ""
    scope = ""
    band = ""
    method = ""
    obj = ""
    filtr = ""
    property_name_array = np.array(["date", "scope", "band", "method", "object"])
    def __init__(self, data):
        self.fits_name = fits_name
        self.data = data
        self.sigma = self.get_sigma()
        paras, cov = hist_gaussian_fitting('default', data)
        self.bkg = paras[0]
        self.std = paras[1]
        return
    # This def is used to find the average sigma of a star
    def get_sigma(self):
        data = self.data
        # peak list is a list contain elements with position tuple.
        sz = 30
        tl = 5
        peak_list = get_peak_filter(data, tall_limit = tl,  size = sz)
        # star list is a list contain elements with star in this fits
        hwl = 4
        ecc = 1
        star_list = get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc)
        proper_star_list = self.proper_sigma(star_list, 3, 4)
        x_sigma = np.array([column[3] for column in proper_star_list])
        y_sigma = np.array([column[4] for column in proper_star_list])
        sigma = np.average([x_sigma, y_sigma], axis = None)
        return sigma
    # find coordinate and flux of a star by aperture photometry.
    def proper_sigma(self, star_list, pos_xsigma, pos_ysigma):
        # in x direction
        x_sigma = [column[pos_xsigma] for column in star_list]
        proper_x_sigma, proper_star_list = get_rid_of_exotic_vector(x_sigma, star_list, 3)
        # in y direction
        y_sigma = [column[pos_ysigma] for column in proper_star_list]
        proper_y_sigma, proper_star_list = get_rid_of_exotic_vector(y_sigma, proper_star_list, 3)
        return proper_star_list
    # get property of images from path
    def observator_property(self, image_name):
    	# get info from name
        image_name_list = image_name.split("_")
    	try:
            self.scope = image_name_list[0]
            self.date = image_name_list[1]
            self.obj = image_name_list[2]
            self.band = image_name_list[3]
            self.filtr = "{0}_{1}".format(image_name_list[3], image_name_list[4])
        # if name is not formated, get info from path	
        except:
            print "Inproper name, get property changing ot dir"
            path = os.getcwd()
            list_path = path.split("/")
            self.scope = list_path[-5]
            self.date = list_path[-3]
            self.obj = list_path[-2]
            self.filtr = list_path[-1]
            temp_list = self.filtr.split("_")
            self.band = temp_list[0]
    	self.method = image_name_list[-2]
    	return

# This class is for find the coordinate of stars and save region file by aperture photometry.
class aperphot(parameter):
    data = None
    dao_table = None
    star_table = None
    def __init__(self, paras, data):
        self.data = data
        # find peak by dao finder
        daofind = DAOStarFinder(threshold = 3.0*paras.std, fwhm=paras.sigma*gaussian_sigma_to_fwhm, roundhi=5.0, roundlo=-5.0, sharplo=0.0, sharphi=2.0, sky = paras.bkg)
        dao_table = daofind.find_stars(paras.data)
        if VERBOSE>2: print dao_table
        self.dao_table = dao_table
        # do aperture photometry
        self.star_table = self.fit()
        return
    def fit(self):
        dao_table = self.dao_table
        data = self.data
        x_list = [int(i) for i in dao_table["ycentroid"]]
        y_list = [int(i) for i in dao_table["xcentroid"]]
        peak_list = zip(x_list, y_list)
        hwl = 3
        ecc = 1
        star_list = get_star(data, peak_list, half_width_lmt = hwl, eccentricity = ecc, detailed = True, VERBOSE = 1)
        # exclude some star will weird sigma
        proper_star_list = self.proper_sigma(star_list, 6, 8)
        if VERBOSE>1:
            print "number of star = {0}".format(len(star_list))
            print "number of proper star = {0}".format(len(proper_star_list))
        # set the unit and title of params in table
        star_title = get_star_title(detailed = True)
        star_unit = get_star_unit(detailed = True)
        star_table = Table(rows = proper_star_list, names = star_title)
        for i in xrange(len(star_unit)):
            star_table[star_title[i]].unit = star_unit[i]
        self.star_table = star_table
        return star_table

# This is a class for save star table and star region file by psf photometry.
class psfphot(parameter):
    data = None
    psf_model = None
    dao_table = None
    star_table = None
    VERBOSE = 0
    def __init__(self, data):
        self.data = data
        self.psf_model = make_model(data)
        self.star_table = self.fit(data)
        return
    def make_model(self):
        # collect normalized bright star
        # if the position is not in the center of pixel, do convolution.
        # take median of all 
        # to 2-D gaussian fitting on psf_model
        psf_model = None
        return psf_model
    def fit(self, data):
        # deconvolution the data by inpulse response.
        # then return source image and star table
        star_table = None
        return star_table
    def convolution(self, psf_model, rect_func):
        # do convolution of psf_model and rect_func
        return con_psf_model

# This class is for control processing photometry
# There are two options, psfphot and aperphot.

# 1. aperphot mean aperture photometry, but not classical, 
# program will fitting 2D gaussian distribution on each peak to test whether it is a star?

# 2. psfphot mean psf photometry,
# This part haven't been done.
class phot_control:
    data = None
    dao_table = None
    star_table = None
    mag_table = None
    paras = None
    fits_name = "untitle.fits"
    star_table_name = "untitle_table.fits"
    result_region_name = "untitle_region"
    dao_table_name = "untitle_dao_table.fits"
    dao_region_name = "untitle_dao_region"
    def __init__(self, fits_name):
        if VERBOSE>0: print "---      start process      ---" 
        # name setting
        self.fits_name = fits_name
        self.data = pyfits.getdata(fits_name)
        self.star_table_name = "{0}_table.fits".format(self.fits_name[0:-5])
        self.result_region_name = "{0}_region".format(self.fits_name[0:-5])
        self.dao_table_name = "{0}_dao_table.fits".format(self.fits_name[0:-5])
        self.dao_region_name = "{0}_dao_region".format(self.fits_name[0:-5])
        # test aperphot is better or psfphot?
        self.paras = parameter(self.data)
        self.paras.observator_property(fits_name)
        #self.star_table, self.dao_table = self.aperphot(self.paras, self.data)
        
        self.star_table, self.dao_table = self.psfphot()
        # get info of del mag
        path_of_result = get_path("path_of_result")
        path_of_del_mag = "{0}/{1}".format(path_of_result, "limitation_magnitude_and_noise/delta_mag.fits")
        del_mag_table = Table.read(path_of_del_mag)
        # add more property info table
        self.match_del_mag_table = self.observertory_property(del_mag_table, self.paras)
        wcs_ctrl = wcs_controller(self.star_table, self.match_del_mag_table, fits_name)
        self.mag_table = wcs_ctrl.mag_table
        return
    # get del mag
    def observertory_property(self, del_mag_table, paras):
        if VERBOSE>0: print "------   find match del mag   ------"
        # create a empty list with length of property list
        property_name_array = paras.property_name_array
        property_list = [paras.date, paras.scope, paras.band, paras.method, paras.obj]
        temp_list = [ None for i in range(len(property_name_array)) ]
        # append original list to back
        # It wiil seem as
        # temp_list = [   [], [], [], ... ,[tar_list]  ]
        temp_list.append(del_mag_table)
        for i in xrange(len(property_name_array)):
            if VERBOSE>0:print "current property = ",property_list[i]
            for tar in temp_list[i-1]:
                if tar[property_name_array[i]] == property_list[i]:
                    if temp_list[i] == None:
                        temp_list[i] = Table(tar)
                    else:
                        temp_list[i].add_row(tar)
        if len(temp_list[len(property_list)-1]) == 0:
            if VERBOSE>0:print "No matched data."
            return None
        match_del_mag_table = temp_list[len(property_list)-1]
        if VERBOSE>0: print match_del_mag_table 
        return match_del_mag_table
    # this def is for cut origin image into several piece. 
    # In order to get much more accurate psf model and fitting result.
    def puzzing(self, data):
        # some constant of puzzle
        img_x_size = len(data)
        img_y_size = len(data[0])
        piece_num = 5
        # parameters we used, include 2D list of puzz data, the position of cut in x and y axis.
        puzz_data = [[None for j in range(piece_num)] for i in range(piece_num)]
        self.x_cut = [img_x_size * i /4 for i in range(piece_num)]
        self.y_cut = [img_y_size * i /4 for i in range(piece_num)]
        for i in xrange(img_x_size-1):
            for j in xrange(img_y_size-1):
                puzz_data[i][j] = data[self.x_cut[i]:self.x_cut[i+1], self.y_cut[j]:self.y_cut[j+1]]
        return puzz_data
    # do psf fitting, powered by psfphot.
    def psfphot(self, data):
        if VERBOSE>0: print "---      psfphot star      ---"
        star_table = None
        puzz_data = self.puzzing(data)
        for i in xrange(puzz_data):
            for j in xrange(puzz_data[i]):
                psffitting = psfphot(puzz_data[i][j])
                star_table = psffitting.star_table
                if star_table == None:
                    star_table = temp_star_table
                else:
                    star_table = astropy.table.join(star_table, temp_star_table)
        return star_table
    def aperphot(self, paras, data):
        if VERBOSE>0: print "---      aperphot star      ---"
        aperfitting = aperphot(paras, data)
        star_table = aperfitting.star_table
        dao_table = aperfitting.dao_table
        return star_table, dao_table
    # save result of photometry.
    def save(self):
        if VERBOSE>0: print "---      save table      ---"
        star_table = self.star_table
        dao_table = self.dao_table
        # save table
        self.mag_table.write(self.star_table_name, overwrite = True)
        # save star region
        region_file = open(self.result_region_name, "a")
        x_list = star_table["ycenter"]
        y_list = star_table["xcenter"]
        for i in xrange(len(x_list)):
            region_file.write("{0} {1}\n".format(x_list[i], y_list[i]))
        region_file.close()
        # save dao table
        dao_table.write(self.dao_table_name, overwrite = True)
        # save dao region
        region_file = open(self.dao_region_name, "a")
        x_list = dao_table["xcentroid"]
        y_list = dao_table["ycentroid"]
        for i in xrange(len(x_list)):
            region_file.write("{0} {1}\n".format(x_list[i], y_list[i]))
        region_file.close()
        return

# This is a code to control pywcs
class wcs_controller(unit_converter):
    star_table = None
    wcs_table = None
    inst_table = None
    mag_table = None
    match_del_mag_table = None
    fits_name = ""
    def __init__(self, star_table, match_del_mag_table, fits_name):
        if VERBOSE>0: print "---      start to process wcs      ---"
        self.fits_name = fits_name
        self.star_table = star_table
        self.match_del_mag_table = match_del_mag_table
        # get wcs coords
        self.wcs_table = self.pix2wcs(star_table, fits_name)
        # get instrument mag
        self.inst_table = self.pix2mag(self.wcs_table, fits_name)
        # get real mag
        self.mag_table = self.realmag(self.inst_table, match_del_mag_table)
        return
    # convert star table into wcs table
    def pix2wcs(self, star_table, fits_name):
        if VERBOSE>0: print "------   convert pixel to wcs   ------"
        # initialized wcs
        try:
            hdulist = pyfits.open(fits_name)
            wcs = pywcs.WCS(hdulist[0].header)
        except:
            print "{0} have no wcs file".format(name)
            return None
        # convert pixel to wcs
        # initialized info
        column_name = ["RAJ2000", "e_RAJ2000", "DECJ2000", "e_DECJ2000"]
        collection = { 'RA':None, 'DEC':None, 'e_RA':None, 'e_DEC':None}
        column_unit = ['hhmmss', 'hhmmss', 'ddmmss', 'ddmmss']
        wcs_table = star_table
        # grap data from table
        xcenter = np.array(star_table["ycenter"], dtype = float)
        e_xcenter = np.array(star_table["e_ycenter"], dtype = float)
        ycenter = np.array(star_table["xcenter"], dtype = float)
        e_ycenter = np.array(star_table["e_xcenter"], dtype = float)
        # arrange data
        coors = np.dstack((xcenter, ycenter))
        '''
        print coors
        print type(coors)
        print coors[0]
        print type(coors[0])
        print coors[0][0]
        print type(coors[0][0])
        '''
        eRA_coors = np.dstack((xcenter + e_xcenter, ycenter)) 
        eDEC_coors = np.dstack((xcenter, ycenter + e_ycenter))
        # convert pixel into wcs
        sky = wcs.wcs_pix2sky(coors[0], 1)	
        collection['RA'] = np.array([column[1] for column in sky])  					# result 1
        collection['DEC'] = np.array([column[0] for column in sky])		    			# result 2
        eRA_sky = wcs.wcs_pix2sky(eRA_coors[0], 1)
        eDEC_sky = wcs.wcs_pix2sky(eDEC_coors[0], 1)
        collection['e_RA'] = np.array([column[1] for column in eRA_sky]) - collection['RA']		# result 3
        collection['e_DEC'] = np.array([column[0] for column in eDEC_sky]) - collection['DEC']		# result 4
        i = 0
        for key, value in collection.iteritems():
            new_col = Column(value, name=column_name[i], unit = column_unit[i])
            wcs_table.add_column(new_col, index = i)
            i += 1	
        return wcs_table
    # convert pixel to instrument mag      <--- haven't divided by exptime
    def pix2mag(self, star_table, fits_name):
        if VERBOSE>0: print "------   convert count to mag   ------"
        # initailized info
        column_name = ["mag", "e_mag"]
        collection = { 'mag':None, 'e_mag':None} 
        column_unit = ['mag_per_sec', 'mag_per_sec']
        # grab data from argument
        mag_table = star_table
        imh = pyfits.getheader(fits_name)
        exptime = imh["EXPTIME"]
        # convert count into mag
        count_per_t = np.array(star_table["amplitude"], dtype = float)/exptime
        e_count_per_t = np.array(star_table["e_amplitude"], dtype = float)/exptime
        mag, e_mag = self.count2mag(count_per_t, e_count_per_t)	
        collection['mag'] = mag
        collection['e_mag'] = e_mag
        # save result into table
        if all([x == np.nan for x in mag]) or all([x == np.nan for x in e_mag]):
            return None
        i = 0
        for key, value in collection.iteritems():
            new_col = Column(value, name=column_name[i], unit=column_unit[i])
            mag_table.add_column(new_col, index = len(mag_table[0]))
            i += 1
        return mag_table
    # get real magnitude
    def realmag(self, star_table, match_del_mag_table):
        if VERBOSE>0: print "------   convert inst mag to real mag   ------"
        # initailized info 
        local_name = ['U', 'B', 'V', 'R', 'I', 'N']
        mag_unit = 'mag_per_sec'
        # grab data from argument
        mag_array = np.array(star_table['mag'], dtype = float)
        e_mag_array = np.array(star_table['e_mag'], dtype = float)
        band_list = match_del_mag_table['band']
        del_mag_array = np.array(match_del_mag_table['delta_mag'], dtype = float)
        e_del_mag_array = np.array(match_del_mag_table['e_delta_mag'], dtype = float)
        mag_table = star_table
        for i in xrange(len(band_list)):
            print "This is {0} round, band is {1}".format(i+1, band_list[i])
            new_mag_name = "{0}_mag".format(band_list[i])
            e_new_mag_name = "e_{0}_mag".format(band_list[i])
            new_mag_array = mag_array - del_mag_array[i]
            e_new_mag_array = np.sqrt(np.power((e_mag_array), 2) + np.power(e_del_mag_array, 2)) # <--- It is wrong now.
            new_col = Column(new_mag_array, name = new_mag_name, unit = mag_unit)
            mag_table.add_column(new_col, index = len(mag_table[0]))
            e_new_col = Column(e_new_mag_array, name = e_new_mag_name, unit = mag_unit)
            mag_table.add_column(e_new_col, index = len(mag_table[0]))
        return mag_table

#--------------------------------------------
# main code
if __name__ == "__main__":
    VERBOSE = 1
    warnings.filterwarnings("ignore")
    # measure times
    start_time = time.time()
    # get property from argv
    fits_name=argv[-1]
    phot = phot_control(fits_name)
    phot.save()
    # measuring time
    elapsed_time = time.time() - start_time
    print "Exiting Main Program, spending ", elapsed_time, "seconds."
